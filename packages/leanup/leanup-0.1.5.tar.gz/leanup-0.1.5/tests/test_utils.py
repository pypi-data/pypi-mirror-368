import subprocess
import pytest
from unittest.mock import patch, Mock
from pathlib import Path
from leanup.const import OS_TYPE
from leanup.utils.basic import execute_command
from leanup.utils.custom_logger import setup_logger


class TestExecuteCommand:
    """Test cases for execute_command function"""
    
    @patch('subprocess.Popen')
    def test_execute_command_success(self, mock_popen):
        """Test successful command execution"""
        mock_process = Mock()
        mock_process.communicate.return_value = ('output', '')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        stdout, stderr, code = execute_command(['echo', 'hello'])
        
        assert stdout == 'output'
        assert stderr == ''
        assert code == 0
    
    @patch('subprocess.Popen')
    def test_execute_command_with_error(self, mock_popen):
        """Test command execution with error"""
        mock_process = Mock()
        mock_process.communicate.return_value = ('', 'error message')
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        stdout, stderr, code = execute_command(['false'])
        
        assert stdout == ''
        assert stderr == 'error message'
        assert code == 1
    
    @patch('subprocess.Popen')
    def test_execute_command_with_cwd(self, mock_popen):
        """Test command execution with working directory"""
        mock_process = Mock()
        mock_process.communicate.return_value = ('output', '')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        execute_command(['ls'], cwd='/tmp')
        
        mock_popen.assert_called_once_with(
            ['ls'],
            cwd='/tmp',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell= OS_TYPE == 'Windows'
        )


class TestSetupLogger:
    """Test cases for setup_logger function"""
    
    def test_setup_logger_basic(self):
        """Test basic logger setup"""
        logger = setup_logger('test_logger')
        
        assert logger.name == 'test_logger'
        assert logger.level == 20  # INFO level
    
    def test_setup_logger_with_file(self, temp_dir):
        """Test logger setup with file output"""
        if OS_TYPE == 'Windows':
            return True
        log_file = temp_dir / 'test.log'
        logger = setup_logger('test_logger', log_file=str(log_file))
        
        logger.info('test message')
        
        assert log_file.exists()
        content = log_file.read_text()
        assert 'test message' in content