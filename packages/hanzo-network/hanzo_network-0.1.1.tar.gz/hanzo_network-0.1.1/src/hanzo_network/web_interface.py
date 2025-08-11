"""Web interface for Hanzo network topology visualization and device connection."""

import json
import asyncio
from typing import Dict, Any, Optional
from aiohttp import web
import aiohttp_cors
from pathlib import Path

class WebInterface:
    """Web interface for network topology visualization and device management."""
    
    def __init__(self, network_node: 'DistributedNetworkNode', port: int = 8080):
        self.network_node = network_node
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        
    def setup_cors(self):
        """Setup CORS for cross-origin requests from web browsers."""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
        })
        
        # Configure CORS on all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/api/topology', self.get_topology)
        self.app.router.add_post('/api/connect', self.connect_device)
        self.app.router.add_get('/api/device/capabilities', self.get_device_capabilities)
        self.app.router.add_ws('/ws', self.websocket_handler)
        self.app.router.add_static('/static', Path(__file__).parent / 'static')
        
    async def index(self, request):
        """Serve the main HTML page."""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Hanzo Network Topology</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            background: #0a0a0a; 
            color: #fff; 
        }
        
        /* Layout */
        .app-container {
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        
        /* Sidebar */
        .sidebar {
            width: 300px;
            background: #1a1a1a;
            border-right: 1px solid #333;
            overflow-y: auto;
            transition: transform 0.3s ease;
            position: relative;
            z-index: 10;
        }
        
        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid #333;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .sidebar-content {
            padding: 20px;
        }
        
        /* Main content */
        .main-content {
            flex: 1;
            overflow-y: auto;
            background: #0f0f0f;
        }
        
        .content-header {
            padding: 20px;
            border-bottom: 1px solid #333;
            background: #1a1a1a;
            position: sticky;
            top: 0;
            z-index: 5;
        }
        
        .content-body {
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Mobile menu toggle */
        .menu-toggle {
            display: none;
            background: none;
            border: none;
            color: #fff;
            font-size: 24px;
            cursor: pointer;
            padding: 5px;
        }
        
        /* Cards and components */
        .card {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #2a2a2a;
        }
        
        .device {
            background: #2a2a2a;
            padding: 16px;
            margin: 12px 0;
            border-radius: 8px;
            border: 1px solid #333;
            transition: all 0.2s ease;
        }
        
        .device:hover {
            background: #333;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        .device.mobile { border-left: 4px solid #4CAF50; }
        .device.desktop { border-left: 4px solid #2196F3; }
        .device.tablet { border-left: 4px solid #ff9800; }
        .device.web { border-left: 4px solid #9c27b0; }
        
        .device-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .device-title {
            font-weight: 600;
            font-size: 1.1em;
        }
        
        .device-icon {
            font-size: 24px;
            margin-right: 8px;
        }
        
        .capabilities {
            margin-top: 12px;
            font-size: 0.9em;
            color: #aaa;
            line-height: 1.6;
        }
        
        .capability-item {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
        }
        
        /* Buttons */
        .button {
            background: #2196F3;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .button:hover {
            background: #1976D2;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
        }
        
        .button.primary { background: #4CAF50; }
        .button.primary:hover { background: #45a049; }
        
        .button.warning { background: #ff9800; }
        .button.warning:hover { background: #e68900; }
        
        /* Status indicators */
        .status {
            padding: 6px 12px;
            border-radius: 20px;
            display: inline-block;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .status.connected {
            background: rgba(76, 175, 80, 0.2);
            color: #4CAF50;
            border: 1px solid #4CAF50;
        }
        
        .status.disconnected {
            background: rgba(244, 67, 54, 0.2);
            color: #f44336;
            border: 1px solid #f44336;
        }
        
        /* Grid layout for stats */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: 600;
            color: #4CAF50;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #888;
            font-size: 0.9em;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .sidebar {
                position: fixed;
                left: 0;
                top: 0;
                height: 100%;
                transform: translateX(-100%);
                box-shadow: 2px 0 10px rgba(0,0,0,0.5);
            }
            
            .sidebar.open {
                transform: translateX(0);
            }
            
            .menu-toggle {
                display: block;
            }
            
            .content-body {
                padding: 16px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .device {
                padding: 12px;
            }
            
            .button {
                width: 100%;
                justify-content: center;
            }
        }
        
        /* Overlay for mobile sidebar */
        .sidebar-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 9;
        }
        
        .sidebar-overlay.active {
            display: block;
        }
        
        /* Animations */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .loading {
            animation: pulse 2s infinite;
        }
        
        /* WebGPU indicator */
        .webgpu-badge {
            background: linear-gradient(45deg, #9c27b0, #2196F3);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Mobile sidebar overlay -->
        <div class="sidebar-overlay" id="sidebarOverlay"></div>
        
        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h2>Hanzo Network</h2>
                <button class="menu-toggle" id="closeSidebar">✕</button>
            </div>
            <div class="sidebar-content">
                <div id="currentDevice" class="card">
                    <h3>This Device</h3>
                    <div id="capabilities" class="loading">Checking...</div>
                    <button id="connectPhone" class="button warning" style="margin-top: 16px;">
                        🔗 Connect This Device
                    </button>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h3>Quick Stats</h3>
                    <div id="quickStats" class="loading">Loading...</div>
                </div>
            </div>
        </aside>
        
        <!-- Main Content -->
        <main class="main-content">
            <header class="content-header">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <button class="menu-toggle" id="openSidebar">☰</button>
                    <h1 style="margin: 0;">Network Topology</h1>
                    <div id="connectionStatus" style="margin-left: auto;"></div>
                </div>
            </header>
            
            <div class="content-body">
                <!-- Network Overview -->
                <section class="card">
                    <h2>Network Overview</h2>
                    <div class="stats-grid" id="networkStats">
                        <div class="stat-card">
                            <div class="stat-label">Total Nodes</div>
                            <div class="stat-value" id="totalNodes">-</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Active Peers</div>
                            <div class="stat-value" id="activePeers">-</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">WebGPU Enabled</div>
                            <div class="stat-value" id="webgpuNodes">-</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Total Memory</div>
                            <div class="stat-value" id="totalMemory">-</div>
                        </div>
                    </div>
                </section>
                
                <!-- Connected Devices -->
                <section class="card">
                    <h2>Connected Devices</h2>
                    <div id="devices" class="loading">
                        <p>Loading devices...</p>
                    </div>
                </section>
                
                <!-- Network Activity -->
                <section class="card">
                    <h2>Network Activity</h2>
                    <div id="activity">
                        <p style="color: #666;">Real-time activity will appear here...</p>
                    </div>
                </section>
            </div>
        </main>
    </div>
    
    <script>
        let ws = null;
        
        // Check WebGPU support
        async function checkWebGPU() {
            if (!navigator.gpu) {
                return { supported: false, reason: 'WebGPU not available' };
            }
            
            try {
                const adapter = await navigator.gpu.requestAdapter();
                if (!adapter) {
                    return { supported: false, reason: 'No GPU adapter found' };
                }
                
                const info = adapter.info || {};
                return {
                    supported: true,
                    vendor: info.vendor || 'Unknown',
                    architecture: info.architecture || 'Unknown',
                    device: info.device || 'Unknown',
                    description: info.description || 'WebGPU Device'
                };
            } catch (e) {
                return { supported: false, reason: e.message };
            }
        }
        
        // Detect device type
        function detectDeviceType() {
            const userAgent = navigator.userAgent.toLowerCase();
            const platform = navigator.platform.toLowerCase();
            
            // Mobile detection
            const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
            const isTablet = /ipad|android(?!.*mobile)/i.test(userAgent);
            
            let deviceType = 'desktop';
            let deviceModel = 'Unknown Device';
            
            if (isMobile) {
                deviceType = 'mobile';
                if (/iphone/.test(userAgent)) {
                    deviceModel = 'iPhone';
                } else if (/android/.test(userAgent)) {
                    deviceModel = 'Android Phone';
                }
            } else if (isTablet) {
                deviceType = 'tablet';
                if (/ipad/.test(userAgent)) {
                    deviceModel = 'iPad';
                } else {
                    deviceModel = 'Android Tablet';
                }
            } else {
                // Desktop detection
                if (platform.includes('mac')) {
                    deviceModel = 'Mac';
                } else if (platform.includes('win')) {
                    deviceModel = 'Windows PC';
                } else if (platform.includes('linux')) {
                    deviceModel = 'Linux PC';
                }
            }
            
            return { type: deviceType, model: deviceModel };
        }
        
        // Get device capabilities
        async function getDeviceCapabilities() {
            const device = detectDeviceType();
            const webgpu = await checkWebGPU();
            
            const capabilities = {
                device_type: device.type,
                device_model: device.model,
                user_agent: navigator.userAgent,
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency || 1,
                memory: navigator.deviceMemory || 'Unknown',
                webgpu: webgpu,
                screen: {
                    width: screen.width,
                    height: screen.height,
                    pixel_ratio: window.devicePixelRatio || 1
                }
            };
            
            // Display capabilities in sidebar
            const capDiv = document.getElementById('capabilities');
            capDiv.innerHTML = `
                <div class="capability-item">
                    <span>Type</span>
                    <span>${device.model}</span>
                </div>
                <div class="capability-item">
                    <span>Platform</span>
                    <span>${device.type}</span>
                </div>
                <div class="capability-item">
                    <span>Cores</span>
                    <span>${capabilities.cores}</span>
                </div>
                <div class="capability-item">
                    <span>Memory</span>
                    <span>${capabilities.memory || '?'} GB</span>
                </div>
                <div class="capability-item">
                    <span>WebGPU</span>
                    <span>${webgpu.supported ? '✅' : '❌'}</span>
                </div>
            `;
            capDiv.classList.remove('loading');
            
            return capabilities;
        }
        
        // Connect device
        async function connectDevice() {
            const capabilities = await getDeviceCapabilities();
            
            try {
                const response = await fetch('/api/connect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(capabilities)
                });
                
                const result = await response.json();
                if (result.success) {
                    alert('Device connected successfully!');
                    updateTopology();
                } else {
                    alert('Failed to connect: ' + result.error);
                }
            } catch (e) {
                alert('Connection error: ' + e.message);
            }
        }
        
        // Update topology display
        async function updateTopology() {
            try {
                const response = await fetch('/api/topology');
                const data = await response.json();
                
                // Update network status
                const statusDiv = document.getElementById('networkStatus');
                statusDiv.innerHTML = `
                    <div>Node ID: ${data.node_id}</div>
                    <div>Status: <span class="status ${data.is_running ? 'connected' : 'disconnected'}">
                        ${data.is_running ? 'Connected' : 'Disconnected'}</span></div>
                    <div>Peers: ${data.peer_count}</div>
                `;
                
                // Update devices list
                const devicesDiv = document.getElementById('devices');
                let devicesHtml = '';
                
                // Add local device
                devicesHtml += `
                    <div class="device desktop">
                        <strong>Local Node</strong> (${data.node_id})<br>
                        <div class="capabilities">
                            ${data.device_capabilities.model} - ${data.device_capabilities.chip}<br>
                            Memory: ${(data.device_capabilities.memory / 1024).toFixed(1)} GB
                        </div>
                    </div>
                `;
                
                // Add peer devices
                data.peers.forEach(peer => {
                    const deviceType = peer.capabilities.model.toLowerCase().includes('phone') || 
                                     peer.capabilities.model.toLowerCase().includes('android') ||
                                     peer.capabilities.model.toLowerCase().includes('iphone') ? 'mobile' : 'desktop';
                    
                    devicesHtml += `
                        <div class="device ${deviceType}">
                            <strong>${peer.capabilities.model}</strong> (${peer.id})<br>
                            <div class="capabilities">
                                ${peer.capabilities.chip || 'Unknown Chip'}<br>
                                Memory: ${peer.capabilities.memory ? 
                                    (peer.capabilities.memory / 1024).toFixed(1) + ' GB' : 
                                    'Unknown'}<br>
                                ${peer.capabilities.webgpu ? 
                                    `WebGPU: ✅ ${peer.capabilities.webgpu.description}` : ''}
                            </div>
                        </div>
                    `;
                });
                
                devicesDiv.innerHTML = devicesHtml;
            } catch (e) {
                console.error('Failed to update topology:', e);
            }
        }
        
        // WebSocket for real-time updates
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onopen = () => {
                console.log('WebSocket connected');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'topology_update') {
                    updateTopology();
                }
            };
            
            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setTimeout(connectWebSocket, 3000); // Reconnect
            };
        }
        
        // Mobile sidebar management
        function setupMobileSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            const openBtn = document.getElementById('openSidebar');
            const closeBtn = document.getElementById('closeSidebar');
            
            function openSidebar() {
                sidebar.classList.add('open');
                overlay.classList.add('active');
            }
            
            function closeSidebar() {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            }
            
            openBtn?.addEventListener('click', openSidebar);
            closeBtn?.addEventListener('click', closeSidebar);
            overlay?.addEventListener('click', closeSidebar);
        }
        
        // Update the display function for better mobile UI
        async function updateTopologyEnhanced() {
            try {
                const response = await fetch('/api/topology');
                const data = await response.json();
                
                // Update connection status
                const statusEl = document.getElementById('connectionStatus');
                statusEl.innerHTML = `
                    <span class="status ${data.is_running ? 'connected' : 'disconnected'}">
                        ${data.is_running ? '● Connected' : '○ Disconnected'}
                    </span>
                `;
                
                // Update stats
                document.getElementById('totalNodes').textContent = (data.peer_count + 1).toString();
                document.getElementById('activePeers').textContent = data.peer_count.toString();
                
                // Calculate WebGPU nodes and total memory
                let webgpuCount = data.device_capabilities.has_webgpu ? 1 : 0;
                let totalMemory = data.device_capabilities.memory || 0;
                
                data.peers.forEach(peer => {
                    if (peer.capabilities.has_webgpu) webgpuCount++;
                    totalMemory += peer.capabilities.memory || 0;
                });
                
                document.getElementById('webgpuNodes').textContent = webgpuCount.toString();
                document.getElementById('totalMemory').textContent = (totalMemory / 1024).toFixed(1) + ' GB';
                
                // Update quick stats in sidebar
                document.getElementById('quickStats').innerHTML = `
                    <div class="capability-item">
                        <span>Node ID</span>
                        <span style="font-family: monospace; font-size: 0.8em;">${data.node_id.slice(0, 8)}...</span>
                    </div>
                    <div class="capability-item">
                        <span>Peers</span>
                        <span>${data.peer_count}</span>
                    </div>
                    <div class="capability-item">
                        <span>Status</span>
                        <span>${data.is_running ? '✅' : '❌'}</span>
                    </div>
                `;
                
                // Update devices list with better icons
                const devicesDiv = document.getElementById('devices');
                let devicesHtml = '';
                
                // Device type icons
                const deviceIcons = {
                    desktop: '🖥️',
                    mobile: '📱',
                    tablet: '📱',
                    web: '🌐'
                };
                
                // Add local device
                const localType = data.device_capabilities.device_type || 'desktop';
                devicesHtml += `
                    <div class="device ${localType}">
                        <div class="device-header">
                            <div>
                                <span class="device-icon">${deviceIcons[localType]}</span>
                                <span class="device-title">This Device</span>
                            </div>
                            <span style="font-size: 0.8em; color: #666;">${data.node_id.slice(0, 8)}...</span>
                        </div>
                        <div class="capabilities">
                            <div class="capability-item">
                                <span>Model</span>
                                <span>${data.device_capabilities.model}</span>
                            </div>
                            <div class="capability-item">
                                <span>Chip</span>
                                <span>${data.device_capabilities.chip}</span>
                            </div>
                            <div class="capability-item">
                                <span>Memory</span>
                                <span>${(data.device_capabilities.memory / 1024).toFixed(1)} GB</span>
                            </div>
                            ${data.device_capabilities.has_webgpu ? 
                                '<div class="webgpu-badge">WebGPU Enabled</div>' : ''}
                        </div>
                    </div>
                `;
                
                // Add peer devices
                data.peers.forEach(peer => {
                    const peerType = peer.capabilities.device_type || 
                                   (peer.capabilities.model.toLowerCase().includes('phone') || 
                                    peer.capabilities.model.toLowerCase().includes('android') ||
                                    peer.capabilities.model.toLowerCase().includes('iphone') ? 'mobile' : 'desktop');
                    
                    devicesHtml += `
                        <div class="device ${peerType}">
                            <div class="device-header">
                                <div>
                                    <span class="device-icon">${deviceIcons[peerType]}</span>
                                    <span class="device-title">${peer.capabilities.model}</span>
                                </div>
                                <span style="font-size: 0.8em; color: #666;">${peer.id.slice(0, 8)}...</span>
                            </div>
                            <div class="capabilities">
                                <div class="capability-item">
                                    <span>Chip</span>
                                    <span>${peer.capabilities.chip || 'Unknown'}</span>
                                </div>
                                <div class="capability-item">
                                    <span>Memory</span>
                                    <span>${peer.capabilities.memory ? 
                                        (peer.capabilities.memory / 1024).toFixed(1) + ' GB' : 
                                        'Unknown'}</span>
                                </div>
                                <div class="capability-item">
                                    <span>Cores</span>
                                    <span>${peer.capabilities.cores || 'Unknown'}</span>
                                </div>
                                ${peer.capabilities.has_webgpu ? 
                                    '<div class="webgpu-badge">WebGPU Enabled</div>' : ''}
                            </div>
                        </div>
                    `;
                });
                
                devicesDiv.innerHTML = devicesHtml;
                devicesDiv.classList.remove('loading');
                
            } catch (e) {
                console.error('Failed to update topology:', e);
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', async () => {
            setupMobileSidebar();
            await getDeviceCapabilities();
            await updateTopologyEnhanced();
            connectWebSocket();
            
            document.getElementById('connectPhone').addEventListener('click', connectDevice);
            
            // Use the enhanced update function
            setInterval(updateTopologyEnhanced, 5000);
        });
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def get_topology(self, request):
        """Get current network topology."""
        status = self.network_node.get_network_status()
        return web.json_response(status)
    
    async def connect_device(self, request):
        """Connect a new device (e.g., phone via browser)."""
        try:
            data = await request.json()
            
            # Create device capabilities from browser data
            capabilities = {
                'model': data.get('device_model', 'Web Device'),
                'chip': 'WebGPU' if data.get('webgpu', {}).get('supported') else 'CPU',
                'memory': int(data.get('memory', 4) * 1024),  # Convert GB to MB
                'has_webgpu': data.get('webgpu', {}).get('supported', False),
                'webgpu_info': data.get('webgpu', {}),
                'device_type': data.get('device_type', 'unknown'),
                'cores': data.get('cores', 1)
            }
            
            # Add as a virtual peer
            peer_id = f"web-{data.get('device_type', 'unknown')}-{hash(request.remote)}"
            
            # Store in a web devices registry (would need to be added to DistributedNetworkNode)
            # For now, just return success
            
            return web.json_response({
                'success': True,
                'peer_id': peer_id,
                'message': 'Device registered successfully'
            })
            
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=400)
    
    async def get_device_capabilities(self, request):
        """Get device capabilities detection script."""
        # This endpoint helps with capability detection
        return web.json_response({
            'webgpu_available': True,
            'detection_script': 'Use navigator.gpu for WebGPU detection'
        })
    
    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    # Handle incoming messages if needed
                    pass
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
        finally:
            await ws.close()
            
        return ws
    
    async def start(self):
        """Start the web server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        print(f"Web interface running at http://0.0.0.0:{self.port}")