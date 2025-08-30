#!/usr/bin/env node

/**
 * InPlay Football Scraper Server - Continuous Railway Deployment
 * =============================================================
 * Runs continuously on Railway with internal scheduling
 * Based on proven Backend-Scripts-OV architecture
 */

const http = require('http');
const { spawn } = require('child_process');

const port = process.env.PORT || 3000;

// Get UK time for logging
function getUKTime() {
    return new Date().toLocaleString("en-GB", {
        timeZone: "Europe/London",
        hour12: false
    });
}

// Get UK hour for scheduling
function getUKHour() {
    const now = new Date();
    const ukTimeString = now.toLocaleString("en-GB", {
        timeZone: "Europe/London",
        hour12: false,
        hour: '2-digit',
        minute: '2-digit'
    });
    const hour = parseInt(ukTimeString.split(':')[0]);
    console.log(`🌍 UTC: ${now.toISOString()}, UK: ${ukTimeString}, Hour: ${hour}`);
    return hour;
}

// Process queue system (like Backend-Scripts-OV)
let processQueue = [];
let isProcessing = false;

// Track running processes
let scraperRunning = false;
let lastScraperTime = 0;

// Health check endpoint
const server = http.createServer((req, res) => {
    if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'healthy',
            service: 'inplay-football-scraper',
            uptime: process.uptime(),
            timestamp: new Date().toISOString(),
            ukTime: getUKTime(),
            scraperRunning: scraperRunning,
            lastScraperTime: lastScraperTime ? new Date(lastScraperTime).toISOString() : 'never',
            queueLength: processQueue.length
        }));
    } else {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end(`InPlay Football Scraper Server
Status: Running
UK Time: ${getUKTime()}
Scraper Running: ${scraperRunning}
Queue Length: ${processQueue.length}
Uptime: ${Math.floor(process.uptime())} seconds`);
    }
});

server.listen(port, () => {
    console.log(`🚀 InPlay Football Scraper Server running on port ${port}`);
    console.log(`🕐 Started at UK time: ${getUKTime()}`);
    console.log(`🔗 Health check: http://localhost:${port}/health`);
});

// Process queue handler
async function processQueue() {
    if (isProcessing || processQueue.length === 0) return;
    
    isProcessing = true;
    const task = processQueue.shift();
    
    console.log(`🔄 Processing: ${task.name} at ${getUKTime()}`);
    
    try {
        await task.execute();
        console.log(`✅ Completed: ${task.name} at ${getUKTime()}`);
    } catch (error) {
        console.error(`❌ Failed: ${task.name} - ${error.message}`);
    }
    
    isProcessing = false;
    
    // Process next task if any
    if (processQueue.length > 0) {
        setTimeout(processQueue, 1000);
    }
}

// Add task to queue
function addTask(name, executeFunction) {
    processQueue.push({ name, execute: executeFunction });
    processQueue();
}

// Run Python scraper
function runScraper() {
    return new Promise((resolve, reject) => {
        if (scraperRunning) {
            console.log(`⚠️ Scraper already running, skipping this cycle`);
            resolve();
            return;
        }
        
        scraperRunning = true;
        lastScraperTime = Date.now();
        
        console.log(`🏈 Starting InPlay Football scraper at ${getUKTime()}`);
        
        const scraper = spawn('python3', ['inplay_football_scraper.py'], {
            stdio: ['pipe', 'pipe', 'pipe'],
            env: { ...process.env }
        });
        
        let output = '';
        let errorOutput = '';
        
        scraper.stdout.on('data', (data) => {
            const message = data.toString();
            output += message;
            console.log(`📊 SCRAPER: ${message.trim()}`);
        });
        
        scraper.stderr.on('data', (data) => {
            const message = data.toString();
            errorOutput += message;
            console.error(`🚨 SCRAPER ERROR: ${message.trim()}`);
        });
        
        scraper.on('close', (code) => {
            scraperRunning = false;
            
            if (code === 0) {
                console.log(`✅ Scraper completed successfully at ${getUKTime()}`);
                resolve();
            } else {
                console.error(`❌ Scraper failed with code ${code} at ${getUKTime()}`);
                console.error(`Error output: ${errorOutput}`);
                reject(new Error(`Scraper process exited with code ${code}`));
            }
        });
        
        scraper.on('error', (error) => {
            scraperRunning = false;
            console.error(`💥 Scraper process error: ${error.message}`);
            reject(error);
        });
        
        // Timeout after 10 minutes
        setTimeout(() => {
            if (scraperRunning) {
                console.log(`⏰ Scraper timeout, killing process`);
                scraper.kill('SIGTERM');
                scraperRunning = false;
                reject(new Error('Scraper timeout'));
            }
        }, 10 * 60 * 1000);
    });
}

// Continuous scheduling logic - runs as soon as previous finishes
function startContinuousScraping() {
    console.log(`🔄 Starting continuous scraping at ${getUKTime()}`);
    
    async function continuousLoop() {
        while (true) {
            try {
                if (!scraperRunning) {
                    console.log(`🎯 Starting scraper run at ${getUKTime()}`);
                    await runScraper();
                    console.log(`✅ Scraper completed, starting next run immediately...`);
                } else {
                    console.log(`⏳ Scraper still running, waiting 10 seconds...`);
                    await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
                }
            } catch (error) {
                console.error(`❌ Scraper error: ${error.message}`);
                console.log(`🔄 Waiting 30 seconds before retry...`);
                await new Promise(resolve => setTimeout(resolve, 30000)); // Wait 30 seconds on error
            }
        }
    }
    
    // Start the continuous loop
    continuousLoop().catch(error => {
        console.error(`💥 Continuous loop crashed: ${error.message}`);
        // Restart after 60 seconds if the loop crashes
        setTimeout(() => {
            console.log(`🔄 Restarting continuous loop...`);
            startContinuousScraping();
        }, 60000);
    });
}

// Main scheduling function
function startScheduling() {
    console.log(`🕐 Starting CONTINUOUS scheduling system at ${getUKTime()}`);
    
    // Start continuous scraping after 30 seconds
    setTimeout(() => {
        console.log(`🚀 Starting continuous scraper loop...`);
        startContinuousScraping();
    }, 30000);
}

// Error handling
process.on('uncaughtException', (error) => {
    console.error(`💥 Uncaught Exception: ${error.message}`);
    console.error(error.stack);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error(`💥 Unhandled Rejection at:`, promise, 'reason:', reason);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log(`🛑 Received SIGTERM, shutting down gracefully at ${getUKTime()}`);
    server.close(() => {
        console.log(`✅ Server closed at ${getUKTime()}`);
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log(`🛑 Received SIGINT, shutting down gracefully at ${getUKTime()}`);
    server.close(() => {
        console.log(`✅ Server closed at ${getUKTime()}`);
        process.exit(0);
    });
});

// Start the scheduling system
startScheduling();

console.log(`🎯 InPlay Football Scraper Server initialized at ${getUKTime()}`);
console.log(`📋 Scheduling: CONTINUOUS (runs immediately after each completion)`);
console.log(`🔄 Overlap protection: Enabled`);
console.log(`⚡ Ready for continuous operation`);
