const { spawn } = require('child_process');
const http = require('http');

// Configuration
const PORT = process.env.PORT || 3000;
let isRunning = false;

// Create HTTP server for health checks
const server = http.createServer((req, res) => {
    if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            status: 'healthy', 
            scraper_running: isRunning,
            timestamp: new Date().toISOString()
        }));
    } else {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('InPlay Football Scraper - Continuous Mode\n');
    }
});

function runScraper() {
    if (isRunning) {
        console.log('⏳ Scraper already running, skipping...');
        return;
    }

    isRunning = true;
    console.log(`🎯 Starting scraper run at ${new Date().toLocaleString('en-GB', { timeZone: 'Europe/London' })}`);

    const pythonCmd = process.env.RAILWAY_ENVIRONMENT ? 'python' : 'python3';
    const scraper = spawn(pythonCmd, ['inplay_football_scraper.py'], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env }
    });

    let output = '';
    let errorOutput = '';

    scraper.stdout.on('data', (data) => {
        const message = data.toString();
        console.log(`📊 SCRAPER: ${message.trim()}`);
        output += message;
    });

    scraper.stderr.on('data', (data) => {
        const message = data.toString();
        console.log(`🚨 SCRAPER ERROR: ${message.trim()}`);
        errorOutput += message;
    });

    scraper.on('close', (code) => {
        isRunning = false;
        const timestamp = new Date().toLocaleString('en-GB', { timeZone: 'Europe/London' });
        
        if (code === 0) {
            console.log(`✅ Scraper completed successfully at ${timestamp}`);
        } else {
            console.log(`❌ Scraper failed with code ${code} at ${timestamp}`);
            if (errorOutput) {
                console.log('Error output:', errorOutput.slice(-500)); // Last 500 chars
            }
        }

        // Schedule next run immediately after completion (continuous mode)
        console.log('🔄 Scheduling next run immediately...');
        setTimeout(runScraper, 1000); // 1 second delay to prevent overlap
    });

    scraper.on('error', (error) => {
        isRunning = false;
        console.error(`❌ Scraper error: ${error.message}`);
        
        // Retry after 30 seconds on error (faster recovery)
        setTimeout(runScraper, 30 * 1000);
    });
}

// Start server
server.listen(PORT, '0.0.0.0', () => {
    console.log('🚀 InPlay Football Scraper Server - Continuous Mode');
    console.log(`📦 Node.js version: ${process.version}`);
    console.log(`🌍 Platform: ${process.platform}`);
    console.log(`🔌 Using port: ${PORT}`);
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`🔗 Health check: http://0.0.0.0:${PORT}/health`);
    
    // Start first scraper run after 10 seconds (faster startup)
    setTimeout(() => {
        console.log('🚀 Starting initial scraper run...');
        runScraper();
    }, 10000);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('📴 Received SIGTERM, shutting down gracefully...');
    server.close(() => {
        console.log('✅ Server closed');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('📴 Received SIGINT, shutting down gracefully...');
    server.close(() => {
        console.log('✅ Server closed');
        process.exit(0);
    });
});