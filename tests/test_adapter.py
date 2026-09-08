"""Regressions for the observed SSE disconnect and hidden quota-error defects."""
import importlib.util
import io
import itertools
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1] / 'skills/game-event-web-animation/scripts/seethrough_remote.py'
spec=importlib.util.spec_from_file_location('adapter',SCRIPT)
adapter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

class AdapterContracts(unittest.TestCase):
    def test_process_token_takes_precedence(self):
        with patch.dict(adapter.os.environ, {'TEST_HF_TOKEN':'synthetic-process'}), \
             patch.object(adapter,'read_user_token') as user_read:
            self.assertEqual(adapter.load_token('TEST_HF_TOKEN'),'synthetic-process')
            user_read.assert_not_called()
    def test_user_token_used_without_restart(self):
        with patch.dict(adapter.os.environ, {}, clear=True), \
             patch.object(adapter,'read_user_token',return_value='synthetic-user') as user_read:
            self.assertEqual(adapter.load_token('TEST_HF_TOKEN'),'synthetic-user')
            user_read.assert_called_once_with('TEST_HF_TOKEN')
    def test_missing_token_stays_missing(self):
        with patch.dict(adapter.os.environ, {}, clear=True), \
             patch.object(adapter,'read_user_token',return_value=None):
            self.assertIsNone(adapter.load_token('TEST_HF_TOKEN'))
    def test_redirect_is_not_followed(self):
        self.assertIsNone(adapter.NoRedirect().redirect_request(None,None,302,'',{},'https://example.org'))
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.out=Path(self.temp.name)
        self.job={'status':'SUBMITTED','layers_validated':False,'rig_validated':False}
        adapter.save(self.out/'job.json',self.job)
    def tearDown(self):
        self.temp.cleanup()
    def consume(self,messages):
        stream=io.BytesIO(b''.join(('data: '+json.dumps(m)+'\n\n').encode() for m in messages))
        return adapter.consume_queue(self.out,self.job,stream)
    def test_quota_error_is_preserved(self):
        message='You have exceeded your ZeroGPU quota (180s requested vs. 115s left).'
        self.assertEqual(self.consume([{'msg':'process_completed','success':False,
            'output':{'error':message,'title':'ZeroGPU quota exceeded'}}]),2)
        self.assertEqual(self.job['error'],message)
        self.assertEqual(self.job['error_title'],'ZeroGPU quota exceeded')
    def test_stays_connected_past_old_twelve_second_limit(self):
        messages=[{'msg':'heartbeat'},{'msg':'process_starts'},
            {'msg':'process_completed','success':True,'output':{'data':[{'path':'x.psd'},[]]}}]
        with patch.object(adapter.time,'monotonic',side_effect=itertools.count(0,16)):
            self.assertEqual(self.consume(messages),0)
        self.assertEqual(self.job['status'],'RESULT_READY')
        self.assertFalse(self.job['rig_validated'])
    def test_poll_is_local_only(self):
        with patch('sys.argv',['adapter','poll','--out',str(self.out)]), \
             patch.object(adapter,'request',side_effect=AssertionError('Must not connect')), \
             patch('sys.stdout',new_callable=io.StringIO):
            self.assertEqual(adapter.main(),0)
    def test_terminal_failed_poll_is_local_only(self):
        self.job['status']='FAILED'
        adapter.save(self.out/'job.json',self.job)
        with patch('sys.argv',['adapter','poll','--out',str(self.out)]), \
             patch.object(adapter,'request',side_effect=AssertionError('Must not connect')), \
             patch('sys.stdout',new_callable=io.StringIO):
            self.assertEqual(adapter.main(),2)
    def test_missing_psd_is_failure(self):
        self.assertEqual(self.consume([{'msg':'process_completed','success':True,
            'output':{'data':[None,[]]}}]),2)
    def test_eof_is_not_resumable_success(self):
        self.assertEqual(self.consume([]),2)
        self.assertEqual(self.job['status'],'FAILED')
if __name__=='__main__': unittest.main()
