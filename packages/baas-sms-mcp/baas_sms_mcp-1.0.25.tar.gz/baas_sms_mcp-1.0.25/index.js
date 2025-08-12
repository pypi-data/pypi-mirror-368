#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

/**
 * BaaS SMS/MMS MCP Server - Node.js Wrapper
 * 
 * This wrapper script executes the Python MCP server and handles
 * cross-platform compatibility and dependency management.
 */

function findPython() {
    // Try common Python executable names
    const pythonCandidates = ['python3', 'python', 'py'];
    
    for (const pythonCmd of pythonCandidates) {
        try {
            const result = require('child_process').spawnSync(pythonCmd, ['--version'], { 
                stdio: 'pipe',
                encoding: 'utf8'
            });
            
            if (result.status === 0 && result.stdout.includes('Python 3.')) {
                return pythonCmd;
            }
        } catch (error) {
            // Continue trying next candidate
        }
    }
    
    throw new Error('Python 3.10+ required but not found. Please install Python 3.10 or higher.');
}

function installDependencies(pythonCmd) {
    const requirementsPath = path.join(__dirname, 'requirements.txt');
    
    // Try different installation methods for macOS
    const installMethods = [
        // Try with --user flag first
        ['-m', 'pip', 'install', '-r', requirementsPath, '--user', '--quiet'],
        // Try with --break-system-packages for externally-managed environments
        ['-m', 'pip', 'install', '-r', requirementsPath, '--break-system-packages', '--quiet'],
        // Try creating a virtual environment
        ['-m', 'venv', path.join(__dirname, '.venv')]
    ];
    
    // First, try direct pip install methods
    for (let i = 0; i < 2; i++) {
        const installProcess = require('child_process').spawnSync(
            pythonCmd, 
            installMethods[i], 
            { 
                stdio: 'pipe',
                cwd: __dirname
            }
        );
        
        if (installProcess.status === 0) {
            return; // Success
        }
    }
    
    // If direct methods fail, try virtual environment
    const venvPath = path.join(__dirname, '.venv');
    const fs = require('fs');
    
    // Create virtual environment if it doesn't exist
    if (!fs.existsSync(venvPath)) {
        const venvProcess = require('child_process').spawnSync(
            pythonCmd, 
            ['-m', 'venv', venvPath], 
            { stdio: 'pipe', cwd: __dirname }
        );
        
        if (venvProcess.status !== 0) {
            throw new Error('Virtual environment creation failed');
        }
    }
    
    // Install dependencies in virtual environment
    const venvPython = os.platform() === 'win32' 
        ? path.join(venvPath, 'Scripts', 'python.exe')
        : path.join(venvPath, 'bin', 'python');
    
    const venvInstallProcess = require('child_process').spawnSync(
        venvPython, 
        ['-m', 'pip', 'install', '-r', requirementsPath, '--quiet'], 
        { 
            stdio: 'pipe',
            cwd: __dirname
        }
    );
    
    if (venvInstallProcess.status !== 0) {
        throw new Error('Virtual environment dependency installation failed');
    }
}

function checkDependencies(pythonCmd) {
    // First check system Python
    let checkProcess = require('child_process').spawnSync(
        pythonCmd,
        ['-c', 'import mcp, httpx'],
        { stdio: 'pipe', encoding: 'utf8' }
    );
    
    if (checkProcess.status === 0) {
        return pythonCmd; // System Python has dependencies
    }
    
    // Check virtual environment
    const venvPath = path.join(__dirname, '.venv');
    const venvPython = os.platform() === 'win32' 
        ? path.join(venvPath, 'Scripts', 'python.exe')
        : path.join(venvPath, 'bin', 'python');
    
    const fs = require('fs');
    if (fs.existsSync(venvPython)) {
        checkProcess = require('child_process').spawnSync(
            venvPython,
            ['-c', 'import mcp, httpx'],
            { stdio: 'pipe', encoding: 'utf8' }
        );
        
        if (checkProcess.status === 0) {
            return venvPython; // Virtual environment has dependencies
        }
    }
    
    // Install dependencies if not found
    try {
        installDependencies(pythonCmd);
        
        // Return appropriate Python executable
        if (fs.existsSync(venvPython)) {
            return venvPython;
        }
        return pythonCmd;
    } catch (error) {
        throw new Error(`Dependency installation failed: ${error.message}`);
    }
}

function startMCPServer() {
    try {
        // Find Python executable
        const pythonCmd = findPython();
        
        // Check and install dependencies if needed, get correct Python path
        const actualPythonCmd = checkDependencies(pythonCmd);
        
        // Path to the Python MCP server
        const serverPath = path.join(__dirname, 'baas_sms_mcp', 'server.py');
        
        // Validate environment variables (silently)
        const requiredEnvVars = ['BAAS_API_KEY'];
        const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
        
        // Only log to stderr for debugging, not stdout (which interferes with MCP protocol)
        if (missingVars.length > 0) {
            process.stderr.write(`Warning: Missing environment variables: ${missingVars.join(', ')}\n`);
        }
        
        // Start the Python MCP server with stdio for MCP protocol
        const serverProcess = spawn(actualPythonCmd, [serverPath], {
            stdio: 'inherit',
            cwd: __dirname,
            env: process.env
        });
        
        // Handle process events
        serverProcess.on('error', (error) => {
            process.stderr.write(`MCP server startup failed: ${error.message}\n`);
            process.exit(1);
        });
        
        serverProcess.on('exit', (code, signal) => {
            if (signal) {
                process.stderr.write(`MCP server terminated by signal: ${signal}\n`);
            } else if (code !== 0) {
                process.stderr.write(`MCP server exited with code: ${code}\n`);
                process.exit(code);
            }
        });
        
        // Handle termination signals
        process.on('SIGINT', () => {
            serverProcess.kill('SIGINT');
        });
        
        process.on('SIGTERM', () => {
            serverProcess.kill('SIGTERM');
        });
        
    } catch (error) {
        process.stderr.write(`MCP server startup error: ${error.message}\n`);
        process.stderr.write('Troubleshooting steps:\n');
        process.stderr.write('1. Ensure Python 3.10+ is installed\n');
        process.stderr.write('2. Check pip availability\n');
        process.stderr.write('3. Set required environment variables: BAAS_API_KEY\n');
        process.exit(1);
    }
}

// Main execution
if (require.main === module) {
    startMCPServer();
}

module.exports = { startMCPServer };