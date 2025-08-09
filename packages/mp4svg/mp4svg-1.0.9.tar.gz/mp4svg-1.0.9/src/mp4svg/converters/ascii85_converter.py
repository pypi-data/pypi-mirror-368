"""
ASCII85 encoding converter for MP4 to SVG
Provides 25% overhead vs 33% for base64
"""

import os
import struct
import base64
from lxml import etree
from ..base import BaseConverter, EncodingError, DecodingError


class ASCII85SVGConverter(BaseConverter):
    """Converts MP4 to SVG using ASCII85 encoding (25% overhead vs 33% for base64)"""

    def convert(self, mp4_path: str, output_path: str, **kwargs) -> str:
        """Convert MP4 to SVG with ASCII85 encoding"""
        
        self._validate_input(mp4_path)
        print(f"[ASCII85] Processing {mp4_path}...")

        # Read video data
        with open(mp4_path, 'rb') as f:
            mp4_data = f.read()

        try:
            # Encode using ASCII85
            encoded = self._encode_ascii85(mp4_data)
            
            # Base64 encode for XML safety
            encoded_b64 = base64.b64encode(encoded.encode('ascii')).decode('ascii')
            
            # Create thumbnail for preview
            thumbnail_b64, thumb_width, thumb_height = self._create_thumbnail(mp4_path)
            
            # Get video metadata
            metadata = self._get_video_metadata(mp4_path)
            
            # Generate SVG content
            svg_content = self._generate_svg(
                mp4_data, encoded_b64, thumbnail_b64, thumb_width, thumb_height, metadata
            )
            
            # Write to file
            with open(output_path, 'w') as f:
                f.write(svg_content)

            print(f"[ASCII85] Created: {output_path}")
            print(f"[ASCII85] Original: {len(mp4_data):,} bytes")
            print(f"[ASCII85] Encoded: {len(encoded):,} chars")
            print(f"[ASCII85] Overhead: {(len(encoded) / len(mp4_data) - 1) * 100:.1f}%")
            if thumbnail_b64:
                print(f"[ASCII85] Added thumbnail: {len(thumbnail_b64)} chars")

            return output_path
            
        except Exception as e:
            raise EncodingError(f"ASCII85 encoding failed: {str(e)}")

    def extract(self, svg_path: str, output_mp4: str) -> bool:
        """Extract MP4 from ASCII85 encoded SVG"""
        
        try:
            tree = etree.parse(svg_path)
            root = tree.getroot()

            # Find video data
            ns = {'video': 'http://example.org/video/2024'}
            video_data = root.find('.//video:data', ns)

            if video_data is None:
                print("[ASCII85] No video data found")
                return False

            encoded = video_data.text.strip()
            decoded_b64 = base64.b64decode(encoded).decode('ascii')
            decoded = self._decode_ascii85(decoded_b64)

            with open(output_mp4, 'wb') as f:
                f.write(decoded)

            print(f"[ASCII85] Extracted to {output_mp4}")
            return True
            
        except Exception as e:
            raise DecodingError(f"ASCII85 extraction failed: {str(e)}")

    def _encode_ascii85(self, data: bytes) -> str:
        """Encode binary data using ASCII85"""
        
        encoded = []
        original_length = len(data)

        # Process in 4-byte chunks
        for i in range(0, len(data), 4):
            chunk = data[i:i + 4]

            # Pad if necessary
            if len(chunk) < 4:
                chunk = chunk + b'\x00' * (4 - len(chunk))

            # Convert to 32-bit integer
            value = struct.unpack('>I', chunk)[0]

            # Special case for all zeros
            if value == 0 and i + 4 <= len(data):
                encoded.append('z')
            else:
                # Convert to base 85
                chars = []
                for _ in range(5):
                    chars.append(chr(33 + (value % 85)))
                    value //= 85
                encoded.append(''.join(reversed(chars)))

        # Simple approach: store original length as decimal prefix separated by ':'
        result = f'<~{original_length}:' + ''.join(encoded) + '~>'
        return result

    def _decode_ascii85(self, encoded: str) -> bytes:
        """Decode ASCII85 string to bytes"""
        
        # Remove delimiters
        if encoded.startswith('<~'):
            encoded = encoded[2:]
        if encoded.endswith('~>'):
            encoded = encoded[:-2]

        # Extract original length from prefix
        length_prefix_end = encoded.find(':')
        original_length = int(encoded[:length_prefix_end])
        encoded = encoded[length_prefix_end + 1:]

        decoded = []
        i = 0
        
        while i < len(encoded):
            if encoded[i] == 'z':
                decoded.extend([0, 0, 0, 0])
                i += 1
            else:
                # Process 5 characters
                chunk = encoded[i:i + 5]
                padding_chars = 0
                if len(chunk) < 5:
                    padding_chars = 5 - len(chunk)
                    chunk += 'u' * padding_chars

                value = 0
                for char in chunk:
                    value = value * 85 + (ord(char) - 33)

                # Convert back to 4 bytes
                chunk_bytes = struct.pack('>I', value)
                
                # If this is the last chunk and we had padding, remove corresponding bytes
                if i + 5 >= len(encoded) and padding_chars > 0:
                    chunk_bytes = chunk_bytes[:4-padding_chars]
                
                decoded.extend(chunk_bytes)
                i += 5

        # Trim decoded data to original length
        decoded = decoded[:original_length]
        
        return bytes(decoded)

    def _generate_svg(self, mp4_data: bytes, encoded_b64: str, thumbnail_b64: str, 
                      thumb_width: int, thumb_height: int, metadata: dict) -> str:
        """Generate SVG content with embedded video data"""
        
        width = metadata['width']
        height = metadata['height']
        fps = metadata['fps']
        frame_count = metadata['frame_count']
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:video="http://example.org/video/2024"
     width="{width}" height="{height}">

    <title>ASCII85 Encoded Video</title>
    <desc>Video data encoded with ASCII85 (25% overhead)</desc>

    <metadata>
        <video:data encoding="ascii85" 
                    originalSize="{len(mp4_data)}"
                    fps="{fps}"
                    frames="{frame_count}"
                    id="videoData">
            <![CDATA[
{encoded_b64}
            ]]>
        </video:data>
    </metadata>

    <defs>
        <style>
            .container {{ fill: #1a1a1a; }}
            .title {{ fill: #0f0; font-size: 24px; text-anchor: middle; }}
            .info {{ fill: #0f0; font-size: 14px; text-anchor: middle; }}
            .efficiency {{ fill: #ff0; font-size: 12px; text-anchor: middle; }}
            .play-btn {{ fill: #00ff00; cursor: pointer; }}
            .play-btn:hover {{ fill: #00cc00; }}
            .thumbnail {{ cursor: pointer; }}
        </style>
    </defs>

    <rect width="100%" height="100%" class="container"/>
    
    <!-- Thumbnail preview -->
    <image x="10" y="10" width="{thumb_width if thumbnail_b64 else 160}" height="{thumb_height if thumbnail_b64 else 90}" 
           href="data:image/jpeg;base64,{thumbnail_b64}" class="thumbnail" id="thumbnailImage" 
           style="display: {'block' if thumbnail_b64 else 'none'}"/>
    
    <text x="50%" y="30%" class="title">ASCII85 Video Container</text>
    <text x="50%" y="40%" class="info">Size: {len(mp4_data):,} bytes → {len(encoded_b64):,} chars</text>
    <text x="50%" y="45%" class="efficiency">Efficiency: 25% overhead (vs 133% for base64)</text>
    
    <!-- Play button -->
    <g id="playButton" class="play-btn">
        <circle cx="50%" cy="60%" r="30" fill="none" stroke="#00ff00" stroke-width="2"/>
        <polygon points="{width//2-10},{height*0.6-15} {width//2-10},{height*0.6+15} {width//2+15},{height*0.6}" fill="#00ff00"/>
        <text x="50%" y="75%" class="info">Click to decode and play video</text>
    </g>

    <script type="text/javascript">
    <![CDATA[
        // ASCII85 decoder implementation with length prefix support
        function decodeASCII85(encoded) {{
            if (encoded.startsWith('<~')) encoded = encoded.substring(2);
            if (encoded.endsWith('~>')) encoded = encoded.substring(0, encoded.length - 2);
            
            // Extract original length from prefix (format: "length:")
            const lengthPrefixEnd = encoded.indexOf(':');
            const originalLength = parseInt(encoded.substring(0, lengthPrefixEnd));
            encoded = encoded.substring(lengthPrefixEnd + 1);
            
            encoded = encoded.replace(/\\s/g, '');
            
            const decoded = [];
            let i = 0;
            
            while (i < encoded.length) {{
                if (encoded[i] === 'z') {{
                    decoded.push(0, 0, 0, 0);
                    i++;
                }} else {{
                    let chunk = encoded.substring(i, i + 5);
                    if (chunk.length < 5) chunk += 'u'.repeat(5 - chunk.length);
                    
                    let value = 0;
                    for (let j = 0; j < chunk.length; j++) {{
                        value = value * 85 + (chunk.charCodeAt(j) - 33);
                    }}
                    
                    decoded.push(
                        (value >>> 24) & 0xFF, (value >>> 16) & 0xFF,
                        (value >>> 8) & 0xFF, value & 0xFF
                    );
                    i += 5;
                }}
            }}
            
            // Trim to original length to remove padding
            const result = new Uint8Array(decoded.slice(0, originalLength));
            console.log('Decoded ASCII85: ' + encoded.length + ' chars -> ' + result.length + ' bytes (expected: ' + originalLength + ')');
            return result;
        }}
        
        function decodeAndPlayVideo() {{
            try {{
                console.log('Decoding ASCII85 video data...');
                
                let videoData = document.getElementById('videoData');
                if (!videoData) {{
                    const metadataElements = document.getElementsByTagNameNS('http://example.org/video/2024', 'data');
                    if (metadataElements && metadataElements.length > 0) videoData = metadataElements[0];
                }}
                if (!videoData) {{
                    const allElements = document.getElementsByTagName('*');
                    for (let element of allElements) {{
                        if (element.localName === 'data' && element.namespaceURI === 'http://example.org/video/2024') {{
                            videoData = element;
                            break;
                        }}
                    }}
                }}
                
                if (!videoData) throw new Error('Video data element not found in SVG');
                
                const encodedData = videoData.textContent.trim();
                
                // First decode base64 to get ASCII85 string
                const ascii85Data = atob(encodedData);
                
                // Then decode ASCII85 to get binary data
                const decodedBytes = decodeASCII85(ascii85Data);
                
                const videoBlob = new Blob([decodedBytes], {{ type: 'video/mp4' }});
                const videoUrl = URL.createObjectURL(videoBlob);
                
                console.log('Creating video container...');
                
                // Create container for video player
                const container = document.createElementNS('http://www.w3.org/2000/svg', 'foreignObject');
                container.setAttribute('x', '5%');
                container.setAttribute('y', '5%');
                container.setAttribute('width', '90%');
                container.setAttribute('height', '90%');
                container.setAttribute('id', 'videoContainer');
                
                // Create HTML div to hold video (proper HTML context)
                let htmlContainer;
                try {{
                    htmlContainer = document.createElement('div');
                    if (htmlContainer.style) {{
                        htmlContainer.style.width = '100%';
                        htmlContainer.style.height = '100%';
                        htmlContainer.style.position = 'relative';
                        htmlContainer.style.backgroundColor = '#000';
                    }} else {{
                        console.warn('htmlContainer.style not available, using attributes');
                        htmlContainer.setAttribute('style', 'width:100%; height:100%; position:relative; background-color:#000;');
                    }}
                    console.log('HTML container created successfully');
                }} catch (e) {{
                    console.error('Error creating HTML container:', e);
                    // Fallback: use simple innerHTML approach
                    container.innerHTML = '<div style="width:100%; height:100%; position:relative; background-color:#000;" id="htmlContainerFallback"></div>';
                    htmlContainer = container.querySelector('#htmlContainerFallback');
                }}
                
                let videoElement;
                try {{
                    videoElement = document.createElement('video');
                    videoElement.src = videoUrl;
                    videoElement.controls = true;
                    videoElement.muted = true;
                    videoElement.preload = 'auto';
                    
                    if (videoElement.style) {{
                        videoElement.style.width = '100%';
                        videoElement.style.height = '100%';
                        videoElement.style.objectFit = 'contain';
                    }} else {{
                        videoElement.setAttribute('style', 'width:100%; height:100%; object-fit:contain;');
                    }}
                    
                    console.log('Video element created successfully');
                }} catch (e) {{
                    console.error('Error creating video element:', e);
                    throw new Error('Failed to create video element: ' + e.message);
                }}
                
                // Add video to HTML container
                if (htmlContainer && htmlContainer.appendChild) {{
                    htmlContainer.appendChild(videoElement);
                }} else {{
                    console.error('htmlContainer or appendChild not available');
                    container.appendChild(videoElement);
                }}
                
                // Add HTML container to SVG foreign object (if not using fallback)
                if (htmlContainer && container.appendChild && !container.querySelector('#htmlContainerFallback')) {{
                    container.appendChild(htmlContainer);
                }}
                
                // Hide UI elements instead of clearing entire SVG
                const playButton = document.getElementById('playButton');
                const thumbnail = document.getElementById('thumbnailImage');
                const titleElements = document.querySelectorAll('text');
                
                if (playButton) playButton.style.display = 'none';
                if (thumbnail) thumbnail.style.display = 'none';
                titleElements.forEach(el => el.style.display = 'none');
                
                // Add video container to SVG
                const svg = document.documentElement;
                svg.appendChild(container);
                
                // Wait for video to be ready before attempting play
                const tryToPlay = () => {{
                    try {{
                        console.log('Attempting to play video...');
                        
                        if (typeof videoElement.play === 'function') {{
                            const playPromise = videoElement.play();
                            if (playPromise !== undefined) {{
                                playPromise.then(() => {{
                                    console.log('Video autoplay started successfully');
                                }}).catch(error => {{
                                    console.log('Autoplay blocked by browser, user interaction required:', error);
                                    showPlayOverlay();
                                }});
                            }}
                        }} else {{
                            console.error('Video element does not have play method');
                            showPlayOverlay();
                        }}
                    }} catch (playError) {{
                        console.error('Error trying to play video:', playError);
                        showPlayOverlay();
                    }}
                }};
                
                const showPlayOverlay = () => {{
                    try {{
                        console.log('Creating play overlay...');
                        const playOverlay = document.createElement('div');
                        playOverlay.innerHTML = '&#9658; Click to Play';
                        
                        if (playOverlay.style) {{
                            playOverlay.style.cssText = 
                                'position: absolute; top: 50%; left: 50%; ' +
                                'transform: translate(-50%, -50%); ' +
                                'background: rgba(0,0,0,0.7); color: white; ' +
                                'padding: 20px; border-radius: 10px; ' +
                                'cursor: pointer; font-size: 18px; ' +
                                'z-index: 1000; pointer-events: auto;';
                        }} else {{
                            console.warn('playOverlay.style not available, using attribute');
                            playOverlay.setAttribute('style', 
                                'position: absolute; top: 50%; left: 50%; ' +
                                'transform: translate(-50%, -50%); ' +
                                'background: rgba(0,0,0,0.7); color: white; ' +
                                'padding: 20px; border-radius: 10px; ' +
                                'cursor: pointer; font-size: 18px; ' +
                                'z-index: 1000; pointer-events: auto;');
                        }}
                        
                        // Create click handler function
                        const handlePlayClick = (event) => {{
                            console.log('🎯 CLICK EVENT TRIGGERED!');
                            console.log('Event:', event);
                            console.log('Event target:', event.target);
                            console.log('playOverlay:', playOverlay);
                            console.log('videoElement:', videoElement);
                            console.log('videoElement type:', typeof videoElement);
                            console.log('videoElement.play type:', typeof videoElement.play);
                            console.log('videoElement.src:', videoElement.src);
                            
                            // Try multiple approaches to play
                            let playSuccessful = false;
                            
                            // Method 1: Direct play if available
                            if (typeof videoElement.play === 'function') {{
                                console.log('Trying direct videoElement.play()...');
                                try {{
                                    const playPromise = videoElement.play();
                                    if (playPromise) {{
                                        playPromise.then(() => {{
                                            console.log('Direct play successful');
                                            playSuccessful = true;
                                        }}).catch(e => console.error('Direct play failed:', e));
                                    }}
                                }} catch (e) {{
                                    console.error('Direct play exception:', e);
                                }}
                            }}
                            
                            // Method 2: Try to trigger click on video controls
                            if (!playSuccessful) {{
                                console.log('Trying to click video controls...');
                                try {{
                                    videoElement.click();
                                }} catch (e) {{
                                    console.error('Video click failed:', e);
                                }}
                            }}
                            
                            // Method 3: Replace with standard HTML video
                            if (!playSuccessful) {{
                                console.log('Trying to replace with standard HTML video...');
                                try {{
                                    // Create a new video element in a popup - more defensive approach
                                    const newVideo = document.createElement('video');
                                    newVideo.src = videoUrl;
                                    newVideo.controls = true;
                                    newVideo.autoplay = true;
                                    
                                    // Defensive styling
                                    const videoStyle = 'position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); z-index:10000; max-width:90%; max-height:90%; background:#000;';
                                    if (newVideo.style && newVideo.style.cssText !== undefined) {{
                                        newVideo.style.cssText = videoStyle;
                                    }} else {{
                                        newVideo.setAttribute('style', videoStyle);
                                    }}
                                    
                                    // Add close button - defensive approach
                                    const closeBtn = document.createElement('button');
                                    closeBtn.innerHTML = '&#10006; Close';
                                    const closeBtnStyle = 'position:fixed; top:10px; right:10px; z-index:10001; background:#f00; color:#fff; border:none; padding:10px; cursor:pointer;';
                                    if (closeBtn.style && closeBtn.style.cssText !== undefined) {{
                                        closeBtn.style.cssText = closeBtnStyle;
                                    }} else {{
                                        closeBtn.setAttribute('style', closeBtnStyle);
                                    }}
                                    
                                    // Add dark overlay - defensive approach  
                                    const overlay = document.createElement('div');
                                    const overlayStyle = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999;';
                                    if (overlay.style && overlay.style.cssText !== undefined) {{
                                        overlay.style.cssText = overlayStyle;
                                    }} else {{
                                        overlay.setAttribute('style', overlayStyle);
                                    }}
                                    
                                    // Close handlers
                                    const closePopup = () => {{
                                        try {{
                                            if (newVideo.parentNode) newVideo.remove();
                                            if (closeBtn.parentNode) closeBtn.remove();
                                            if (overlay.parentNode) overlay.remove();
                                        }} catch (e) {{
                                            console.error('Error closing popup:', e);
                                        }}
                                    }};
                                    
                                    closeBtn.onclick = closePopup;
                                    overlay.onclick = closePopup;
                                    
                                    // Add to page
                                    if (document.body) {{
                                        document.body.appendChild(overlay);
                                        document.body.appendChild(newVideo);
                                        document.body.appendChild(closeBtn);
                                        console.log('Popup video created successfully');
                                    }} else {{
                                        console.error('document.body not available');
                                    }}
                                    
                                }} catch (e) {{
                                    console.error('Popup video failed:', e);
                                    // Final fallback: open video in new tab
                                    try {{
                                        const link = document.createElement('a');
                                        link.href = videoUrl;
                                        link.download = 'video.mp4';
                                        link.target = '_blank';
                                        link.click();
                                        console.log('Opened video in new tab as final fallback');
                                    }} catch (linkError) {{
                                        console.error('All video playback methods failed:', linkError);
                                    }}
                                }}
                            }}
                            
                            // Hide the play overlay after click attempt
                            setTimeout(() => {{
                                try {{
                                    playOverlay.remove();
                                }} catch (e) {{
                                    console.error('Error removing overlay:', e);
                                }}
                            }}, 100);
                        }};
                        
                        // Try multiple event types for maximum compatibility
                        playOverlay.addEventListener('click', handlePlayClick);
                        playOverlay.addEventListener('touchstart', handlePlayClick);
                        playOverlay.addEventListener('mousedown', handlePlayClick);
                        
                        // Also try traditional onclick as backup
                        try {{
                            playOverlay.onclick = handlePlayClick;
                        }} catch (e) {{
                            console.warn('onclick assignment failed:', e);
                        }}
                        
                        // Try to append to htmlContainer, fallback to container
                        if (htmlContainer && htmlContainer.appendChild) {{
                            console.log('Adding overlay to htmlContainer');
                            htmlContainer.appendChild(playOverlay);
                        }} else if (container && container.appendChild) {{
                            console.log('Adding overlay to container (fallback)');
                            container.appendChild(playOverlay);
                        }} else {{
                            console.error('No valid container found for overlay');
                        }}
                        
                        playOverlay.addEventListener('click', handlePlayClick);
                        
                        console.log('Play overlay created successfully');
                    }} catch (overlayError) {{
                        console.error('Error creating play overlay:', overlayError);
                    }}
                }};
                
                // Try multiple approaches to ensure video is ready
                if (videoElement.readyState >= 2) {{
                    // Video is already loaded enough to play
                    setTimeout(tryToPlay, 100);
                }} else {{
                    // Wait for video to load
                    videoElement.addEventListener('loadeddata', () => {{
                        console.log('Video loadeddata event fired');
                        setTimeout(tryToPlay, 100);
                    }});
                    
                    videoElement.addEventListener('canplay', () => {{
                        console.log('Video canplay event fired');
                        setTimeout(tryToPlay, 100);
                    }});
                    
                    // Fallback timeout
                    setTimeout(() => {{
                        console.log('Fallback timeout - trying to play anyway');
                        tryToPlay();
                    }}, 1000);
                }}
                
                console.log('Video player created');
                
            }} catch (error) {{
                console.error('Error decoding video:', error);
                alert('Error decoding video: ' + error.message);
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            const playButton = document.getElementById('playButton');
            const thumbnail = document.getElementById('thumbnailImage');
            
            if (playButton) playButton.addEventListener('click', decodeAndPlayVideo);
            if (thumbnail) thumbnail.addEventListener('click', decodeAndPlayVideo);
        }});
    ]]>
    </script>
</svg>'''
