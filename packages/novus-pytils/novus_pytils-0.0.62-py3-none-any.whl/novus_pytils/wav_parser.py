"""
A lightweight, dependency-free Python package for parsing WAV audio files.
Supports standard PCM WAV files with proper RIFF structure parsing.
"""

import struct
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path


class WAVError(Exception):
    """Base exception for WAV parsing errors."""
    pass


class InvalidWAVFormatError(WAVError):
    """Raised when WAV file format is invalid or unsupported."""
    pass


class CorruptedFileError(WAVError):
    """Raised when WAV file appears to be corrupted."""
    pass


@dataclass
class WAVFormat:
    """WAV format information."""
    audio_format: int
    channels: int
    sample_rate: int
    byte_rate: int
    block_align: int
    bits_per_sample: int
    
    @property
    def is_pcm(self) -> bool:
        """Check if format is PCM (uncompressed)."""
        return self.audio_format == 1
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration based on byte rate (requires data size)."""
        # This will be set by the parser when data size is known
        return getattr(self, '_duration', 0.0)


@dataclass
class WAVChunk:
    """Represents a RIFF chunk in the WAV file."""
    id: str
    size: int
    data: bytes
    offset: int


class WAVParser:
    """Pure Python WAV file parser."""
    
    def __init__(self, file_path: Union[str, Path]):
        """Initialize parser with file path."""
        self.file_path = Path(file_path)
        self.format_info: Optional[WAVFormat] = None
        self.chunks: Dict[str, WAVChunk] = {}
        self.audio_data: Optional[bytes] = None
        self._file_size = 0
        
    def parse(self) -> Dict:
        """Parse the WAV file and return comprehensive information."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"WAV file not found: {self.file_path}")
        
        self._file_size = self.file_path.stat().st_size
        
        with open(self.file_path, 'rb') as f:
            self._parse_riff_header(f)
            self._parse_chunks(f)
            self._validate_format()
        
        return self.get_info()
    
    def _parse_riff_header(self, f) -> None:
        """Parse the RIFF header."""
        # Read RIFF header (12 bytes)
        riff_header = f.read(12)
        if len(riff_header) != 12:
            raise CorruptedFileError("File too small to be a valid WAV file")
        
        riff_id, file_size, wave_id = struct.unpack('<4sI4s', riff_header)
        
        if riff_id != b'RIFF':
            raise InvalidWAVFormatError("Not a valid RIFF file")
        
        if wave_id != b'WAVE':
            raise InvalidWAVFormatError("Not a valid WAV file")
        
        # Validate file size
        expected_size = file_size + 8
        if expected_size != self._file_size:
            # Some files have incorrect size in header, warn but continue
            pass
    
    def _parse_chunks(self, f) -> None:
        """Parse all chunks in the WAV file."""
        while True:
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break  # End of file
            
            chunk_id, chunk_size = struct.unpack('<4sI', chunk_header)
            chunk_id = chunk_id.decode('ascii', errors='ignore')
            
            # Store current position for chunk data
            chunk_offset = f.tell()
            
            # Read chunk data
            chunk_data = f.read(chunk_size)
            if len(chunk_data) != chunk_size:
                raise CorruptedFileError(f"Incomplete chunk: {chunk_id}")
            
            # Store chunk
            self.chunks[chunk_id] = WAVChunk(
                id=chunk_id,
                size=chunk_size,
                data=chunk_data,
                offset=chunk_offset
            )
            
            # Parse specific chunks
            if chunk_id == 'fmt ':
                self._parse_format_chunk(chunk_data)
            elif chunk_id == 'data':
                self.audio_data = chunk_data
            
            # Align to even byte boundary (WAV spec requirement)
            if chunk_size % 2:
                f.read(1)
    
    def _parse_format_chunk(self, data: bytes) -> None:
        """Parse the format chunk."""
        if len(data) < 16:
            raise InvalidWAVFormatError("Format chunk too small")
        
        # Standard format chunk (16 bytes minimum)
        fmt_data = struct.unpack('<HHIIHH', data[:16])
        
        self.format_info = WAVFormat(
            audio_format=fmt_data[0],
            channels=fmt_data[1],
            sample_rate=fmt_data[2],
            byte_rate=fmt_data[3],
            block_align=fmt_data[4],
            bits_per_sample=fmt_data[5]
        )
        
        # Calculate duration if we have audio data
        if self.audio_data and self.format_info.byte_rate > 0:
            duration = len(self.audio_data) / self.format_info.byte_rate
            self.format_info._duration = duration
    
    def _validate_format(self) -> None:
        """Validate the parsed format."""
        if not self.format_info:
            raise InvalidWAVFormatError("No format chunk found")
        
        if not self.format_info.is_pcm:
            raise InvalidWAVFormatError(
                f"Unsupported audio format: {self.format_info.audio_format} "
                "(only PCM is supported)"
            )
        
        if self.format_info.channels == 0:
            raise InvalidWAVFormatError("Invalid number of channels")
        
        if self.format_info.sample_rate == 0:
            raise InvalidWAVFormatError("Invalid sample rate")
        
        if self.audio_data is None:
            raise InvalidWAVFormatError("No audio data found")
    
    def get_info(self) -> Dict:
        """Get comprehensive information about the WAV file."""
        if not self.format_info:
            raise WAVError("File not parsed yet. Call parse() first.")
        
        info = {
            'file_path': str(self.file_path),
            'file_size': self._file_size,
            'format': {
                'audio_format': self.format_info.audio_format,
                'channels': self.format_info.channels,
                'sample_rate': self.format_info.sample_rate,
                'byte_rate': self.format_info.byte_rate,
                'block_align': self.format_info.block_align,
                'bits_per_sample': self.format_info.bits_per_sample,
                'is_pcm': self.format_info.is_pcm
            },
            'duration_seconds': self.format_info.duration_seconds,
            'audio_data_size': len(self.audio_data) if self.audio_data else 0,
            'sample_count': self._calculate_sample_count(),
            'chunks': {chunk_id: chunk.size for chunk_id, chunk in self.chunks.items()}
        }
        
        return info
    
    def _calculate_sample_count(self) -> int:
        """Calculate total number of samples."""
        if not self.audio_data or not self.format_info:
            return 0
        
        bytes_per_sample = self.format_info.bits_per_sample // 8
        return len(self.audio_data) // (bytes_per_sample * self.format_info.channels)
    
    def get_audio_samples(self, normalize: bool = False) -> List[List[float]]:
        """
        Extract audio samples from the WAV file.
        
        Args:
            normalize: If True, normalize samples to [-1.0, 1.0] range
            
        Returns:
            List of channels, each containing a list of sample values
        """
        if not self.audio_data or not self.format_info:
            raise WAVError("No audio data available")
        
        channels = self.format_info.channels
        bits_per_sample = self.format_info.bits_per_sample
        sample_count = self._calculate_sample_count()
        
        # Determine sample format
        if bits_per_sample == 8:
            fmt = 'B'  # unsigned byte
            offset = 128
            max_val = 127
        elif bits_per_sample == 16:
            fmt = 'h'  # signed short
            offset = 0
            max_val = 32767
        elif bits_per_sample == 24:
            # 24-bit samples need special handling
            return self._parse_24bit_samples(normalize)
        elif bits_per_sample == 32:
            fmt = 'i'  # signed int
            offset = 0
            max_val = 2147483647
        else:
            raise InvalidWAVFormatError(f"Unsupported bit depth: {bits_per_sample}")
        
        # Parse samples
        sample_size = bits_per_sample // 8
        format_str = f'<{sample_count * channels}{fmt}'
        
        samples = struct.unpack(format_str, self.audio_data)
        
        # Organize by channel
        channel_samples = [[] for _ in range(channels)]
        for i, sample in enumerate(samples):
            channel = i % channels
            value = sample - offset
            
            if normalize:
                value = value / max_val
            
            channel_samples[channel].append(value)
        
        return channel_samples
    
    def _parse_24bit_samples(self, normalize: bool = False) -> List[List[float]]:
        """Parse 24-bit samples (special case)."""
        channels = self.format_info.channels
        sample_count = self._calculate_sample_count()
        
        channel_samples = [[] for _ in range(channels)]
        
        for i in range(sample_count):
            for ch in range(channels):
                # Read 3 bytes and convert to signed 24-bit
                offset = (i * channels + ch) * 3
                if offset + 3 > len(self.audio_data):
                    break
                
                bytes_sample = self.audio_data[offset:offset + 3]
                # Convert to signed 24-bit integer
                value = struct.unpack('<I', bytes_sample + b'\x00')[0]
                if value & 0x800000:  # Sign bit set
                    value -= 0x1000000
                
                if normalize:
                    value = value / 8388607  # 2^23 - 1
                
                channel_samples[ch].append(value)
        
        return channel_samples
    
    def export_metadata(self) -> Dict:
        """Export metadata in a structured format."""
        info = self.get_info()
        
        metadata = {
            'basic': {
                'duration': f"{info['duration_seconds']:.2f} seconds",
                'channels': info['format']['channels'],
                'sample_rate': f"{info['format']['sample_rate']} Hz",
                'bit_depth': f"{info['format']['bits_per_sample']} bits",
                'format': 'PCM' if info['format']['is_pcm'] else 'Compressed'
            },
            'technical': {
                'file_size': f"{info['file_size']:,} bytes",
                'audio_data_size': f"{info['audio_data_size']:,} bytes",
                'byte_rate': f"{info['format']['byte_rate']:,} bytes/sec",
                'block_align': info['format']['block_align'],
                'sample_count': f"{info['sample_count']:,} samples"
            },
            'chunks': info['chunks']
        }
        
        return metadata


# Convenience functions
def parse_wav(file_path: Union[str, Path]) -> Dict:
    """
    Quick function to parse a WAV file and return information.
    
    Args:
        file_path: Path to the WAV file
        
    Returns:
        Dictionary containing WAV file information
    """
    parser = WAVParser(file_path)
    return parser.parse()


def get_wav_samples(file_path: Union[str, Path], normalize: bool = True) -> List[List[float]]:
    """
    Quick function to extract audio samples from a WAV file.
    
    Args:
        file_path: Path to the WAV file
        normalize: Whether to normalize samples to [-1.0, 1.0] range
        
    Returns:
        List of channels, each containing sample values
    """
    parser = WAVParser(file_path)
    parser.parse()
    return parser.get_audio_samples(normalize=normalize)


def validate_wav(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a valid WAV file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if valid WAV file, False otherwise
    """
    try:
        parse_wav(file_path)
        return True
    except (WAVError, FileNotFoundError, struct.error):
        return False


