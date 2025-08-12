# Wrapper for the wave library
import wave
import numpy as np
from novus_pytils.files import get_files_by_extension, get_file_name
from novus_pytils.hash import get_file_md5_hash

def get_wav_files(dir):
    """
    Get all WAV files in a directory.

    Args:
        dir (str): The directory to search for WAV files.

    Returns:
        list: A list of paths to WAV files in the directory.
    """
    return get_files_by_extension(dir, ['.wav'])
def read_wav_file(filename):
    """
    Reads a WAV file and returns the audio data and file metadata.

    Args:
        filename (str): The path to the WAV file to read.

    Returns:
        tuple: A tuple containing:
            audio_data (numpy.ndarray): The raw audio data as a NumPy array of int16 values.
            num_channels (int): The number of audio channels in the file (1 for mono, 2 for stereo).
            sample_width (int): The sample width in bytes (1, 2, 3, or 4).
            frame_rate (int): The frame rate of the file in Hz.
            num_frames (int): The total number of frames in the file.
            duration (float): The duration of the file in seconds.
    """
    with wave.open(filename, 'rb') as wav_file:
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        duration = num_frames / frame_rate

        audio_data = np.frombuffer(wav_file.readframes(num_frames), dtype=np.int16)

        return audio_data, num_channels, sample_width, frame_rate, num_frames, duration
    
def get_wav_metadata(wav_filepath : str) -> dict:
    with wave.open(wav_filepath, 'rb') as wav_file:
        return {
            "filepath": wav_filepath,
            "file_size": wav_file.getnframes() * wav_file.getnchannels() * wav_file.getsampwidth(),
            "num_channels": wav_file.getnchannels(),
            "sample_width": wav_file.getsampwidth(),
            "frame_rate": wav_file.getframerate(),
            "num_frames": wav_file.getnframes(),
            "duration": wav_file.getnframes() / wav_file.getframerate()
        }
    
def analyze_wav_file(wav_path, input_dir):
    """
    Analyze a WAV file and extract comprehensive information.
    
    Args:
        wav_path (Path): Path to the WAV file
        input_dir (Path): Input directory path for relative path calculation
    
    Returns:
        dict: Dictionary containing file analysis results
    """
    from pathlib import Path
    wav_path = Path(wav_path)
    file_info = {
        'filename': wav_path.name,
        'relative_path': str(wav_path.relative_to(input_dir)),
        'full_path': str(wav_path),
        'file_size_bytes': 0,
        'file_size_mb': 0.0,
        'sample_rate': 0,
        'num_channels': 0,
        'num_frames': 0,
        'sample_width_bytes': 0,
        'sample_width_bits': 0,
        'length_seconds': 0.0,
        'length_milliseconds': 0,
        'length_formatted': '00:00:00.000',
        'md5_hash': '',
        'compression_type': '',
        'compression_name': '',
        'status': 'Success',
        'error_message': ''
    }
    
    try:
        # Get file size
        file_info['file_size_bytes'] = wav_path.stat().st_size
        file_info['file_size_mb'] = file_info['file_size_bytes'] / (1024 * 1024)
        
        # Open and analyze WAV file
        with wave.open(str(wav_path), 'rb') as wav_file:
            # Get basic parameters
            file_info['num_channels'] = wav_file.getnchannels()
            file_info['sample_rate'] = wav_file.getframerate()
            file_info['num_frames'] = wav_file.getnframes()
            file_info['sample_width_bytes'] = wav_file.getsampwidth()
            file_info['sample_width_bits'] = file_info['sample_width_bytes'] * 8
            file_info['compression_type'] = wav_file.getcomptype()
            file_info['compression_name'] = wav_file.getcompname()
            
            # Calculate duration
            if file_info['sample_rate'] > 0:
                file_info['length_seconds'] = file_info['num_frames'] / file_info['sample_rate']
                file_info['length_milliseconds'] = int(file_info['length_seconds'] * 1000)
                
                # Format duration as HH:MM:SS.mmm
                hours = int(file_info['length_seconds'] // 3600)
                minutes = int((file_info['length_seconds'] % 3600) // 60)
                seconds = file_info['length_seconds'] % 60
                file_info['length_formatted'] = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        
        # Calculate MD5 hash
        file_info['md5_hash'] = get_file_md5_hash(wav_path)
        
    except wave.Error as e:
        file_info['status'] = 'WAV Error'
        file_info['error_message'] = str(e)
    except Exception as e:
        file_info['status'] = 'Error'
        file_info['error_message'] = str(e)
    
    return file_info
    
def get_wav_files_metadata(wav_filepaths : list) -> list:
    """
    Returns the metadata of a list of wav files.
    
    Args:
        wav_filepaths (list): A list of paths to the wav files.
        
    Returns:
        list: A list of dictionaries containing the metadata of the wav files.
    """
    return [get_wav_metadata(wav_file) for wav_file in wav_filepaths]
    
def get_wav_num_channels(filename):
    """
    Reads a WAV file and returns the number of audio channels it contains.

    Args:
        filename (str): The path to the WAV file to read.

    Returns:
        int: The number of audio channels in the file (1 for mono, 2 for stereo).
    """
    with wave.open(filename, 'rb') as wav_file:
        return wav_file.getnchannels()
    
def get_wav_sample_width(filename):
    """
    Reads a WAV file and returns its sample width in bytes.

    Args:
        filename (str): The path to the WAV file to read.

    Returns:
        int: The sample width in bytes (1, 2, 3, or 4).
    """

    with wave.open(filename, 'rb') as wav_file:
        return wav_file.getsampwidth()
    
def get_wav_frame_rate(filename):
    """
    Reads a WAV file and returns its frame rate in Hz.

    Args:
        filename (str): The path to the WAV file to read.

    Returns:
        int: The frame rate of the file in Hz.
    """
    with wave.open(filename, 'rb') as wav_file:
        return wav_file.getframerate()
    
def get_wav_num_frames(filename):
    """
    Reads a WAV file and returns the total number of frames.

    Args:
        filename (str): The path to the WAV file to read.

    Returns:
        int: The total number of frames in the file.
    """

    with wave.open(filename, 'rb') as wav_file:
        return wav_file.getnframes()
    
def get_wav_duration(filename):
    """
    Reads a WAV file and returns its duration in seconds.

    Args:
        filename (str): The path to the WAV file to read.

    Returns:
        float: The duration of the file in seconds.
    """

    with wave.open(filename, 'rb') as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()

def get_wav_data(filename):
    """
    Reads a WAV file and returns its raw audio data.

    Args:
        filename (str): The path to the WAV file to read.

    Returns:
        bytes: The raw audio data from the file.
    """

    with wave.open(filename, 'rb') as wav_file:
        return wav_file.readframes(wav_file.getnframes())
    
def write_wav_file(filename, audio_data, num_channels, sample_width, frame_rate):
    """
    Writes audio data to a WAV file with specified parameters.

    Args:
        filename (str): The path to the output WAV file.
        audio_data (numpy.ndarray): The audio data to write as a NumPy array.
        num_channels (int): The number of audio channels (1 for mono, 2 for stereo).
        sample_width (int): The sample width in bytes (1, 2, 3, or 4).
        frame_rate (int): The frame rate of the audio data in Hz.
    """

    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)
        wav_file.writeframes(audio_data.tobytes())

def convert_array_to_wav(filename, audio_data, num_channels, sample_width, frame_rate):
    """
    Writes a NumPy array of audio data to a WAV file with specified parameters.

    Args:
        filename (str): The path to the output WAV file.
        audio_data (numpy.ndarray): The audio data to write as a NumPy array.
        num_channels (int): The number of audio channels (1 for mono, 2 for stereo).
        sample_width (int): The sample width in bytes (1, 2, 3, or 4).
        frame_rate (int): The frame rate of the audio data in Hz.
    """
    write_wav_file(filename, audio_data, num_channels, sample_width, frame_rate)

def split_wav_file(filename, duration):
    """
    Splits a WAV file into segments of a given duration.

    Args:
        filename (str): The path to the WAV file to split.
        duration (float): The duration of each segment in seconds.

    Returns:
        None
    """
    with wave.open(filename, 'rb') as wav_file:
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()

        audio_data = np.frombuffer(wav_file.readframes(num_frames), dtype=np.int16)

        num_segments = int(np.ceil(num_frames / (duration * frame_rate)))
        segment_length = int(num_frames / num_segments)

        for i in range(num_segments):
            start_frame = i * segment_length
            end_frame = (i + 1) * segment_length
            if i == num_segments - 1:
                end_frame = num_frames

            segment_data = audio_data[start_frame:end_frame]
            segment_filename = f"{filename}_{i}.wav"
            write_wav_file(segment_filename, segment_data, num_channels, sample_width, frame_rate)


