import unittest
import urllib
from main import app


class CommandAppTest(unittest.TestCase):
 
    def setUp(self):
        self.app = app.test_client()
 
    #DB tests
    def test_db_creation(self):
        resp = self.app.post('/database') 
        self.assertEqual(resp.status_code, 200)

    def test_db_deletion(self):
        db_create_resp = self.app.post('/database')   
        self.assertEqual(db_create_resp.status_code, 200)        
        db_del_resp = self.app.delete('/database') 
        self.assertEqual(db_del_resp.status_code, 200)
        
    #commands tests with filename
    def test_commands_success_path_filename(self):
        #create database
        db_create_resp = self.app.post('/database')   
        self.assertEqual(db_create_resp.status_code, 200)   
        #execute few commands
        post_resp =  self.app.post('/commands?filename=commands.txt') 
        self.assertEqual(post_resp.status_code, 200)
        #make sure GET on /command returns 200
        get_resp = self.app.get('/commands') 
        self.assertEqual(get_resp.status_code, 200)

    #commands tests with file_data
    def test_commands_success_path_filedata(self):
        #create database
        db_create_resp = self.app.post('/database')   
        self.assertEqual(db_create_resp.status_code, 200)   
        #execute few commands
        with open("test1_cmds.txt") as f:
            file_data = f.read()
        post_resp =  self.app.post('/commands?file_data={0}'.format(urllib.quote_plus(file_data))) 
        self.assertEqual(post_resp.status_code, 200)
        #make sure GET on /command returns 200
        get_resp = self.app.get('/commands') 
        self.assertEqual(get_resp.status_code, 200)

    def test_getcommands_without_running_postcommands(self):
        get_resp = self.app.get('/commands') 
        self.assertEqual(get_resp.status_code, 400)
    
    # TODO: verify the reponse content/commands metadata from GET /commands
    # e.g number of cmds in response, cmd string length, number of cmds with duration == 1 etc
    

if __name__ == '__main__':
    unittest.main()
