#!/usr/bin/env node
/**
 * WebSocket Connection Test Script
 * 
 * Tests the WebSocket URL accessibility outside of React to isolate connection issues.
 */

const WebSocket = require('ws');

const WEBSOCKET_URL = 'wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev';
const TEST_TIMEOUT = 10000; // 10 seconds

console.log('🔌 WebSocket Connection Test');
console.log('============================');
console.log(`Testing URL: ${WEBSOCKET_URL}`);
console.log(`Timeout: ${TEST_TIMEOUT}ms\n`);

function testWebSocketConnection() {
  return new Promise((resolve, reject) => {
    let connectionAttempted = false;
    let messagesReceived = [];
    let connectionClosed = false;
    
    const startTime = Date.now();
    
    try {
      const ws = new WebSocket(WEBSOCKET_URL);
      
      // Set timeout
      const timeout = setTimeout(() => {
        if (!connectionClosed) {
          console.log('❌ Connection timeout after 10 seconds');
          ws.close();
          reject(new Error('Connection timeout'));
        }
      }, TEST_TIMEOUT);
      
      ws.on('open', () => {
        connectionAttempted = true;
        const connectionTime = Date.now() - startTime;
        console.log(`✅ WebSocket connection established in ${connectionTime}ms`);
        
        // Test sending a message
        const testMessage = {
          action: 'test',
          message: 'Connection test from Node.js',
          timestamp: new Date().toISOString()
        };
        
        console.log('📤 Sending test message:', testMessage);
        ws.send(JSON.stringify(testMessage));
        
        // Wait for response or close after a bit
        setTimeout(() => {
          if (!connectionClosed) {
            console.log('✅ Connection stable, closing gracefully');
            ws.close();
          }
        }, 3000);
      });
      
      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          messagesReceived.push(message);
          console.log('📥 Received message:', message);
        } catch (err) {
          console.log('📥 Received non-JSON message:', data.toString());
        }
      });
      
      ws.on('close', (code, reason) => {
        connectionClosed = true;
        clearTimeout(timeout);
        const totalTime = Date.now() - startTime;
        
        console.log(`🔌 Connection closed after ${totalTime}ms`);
        console.log(`   Code: ${code}`);
        console.log(`   Reason: ${reason || 'No reason provided'}`);
        
        resolve({
          success: connectionAttempted,
          connectionTime: totalTime,
          messagesReceived: messagesReceived.length,
          closeCode: code,
          closeReason: reason?.toString()
        });
      });
      
      ws.on('error', (error) => {
        connectionClosed = true;
        clearTimeout(timeout);
        const errorTime = Date.now() - startTime;
        
        console.log(`❌ WebSocket error after ${errorTime}ms:`, error.message);
        console.log('   Error type:', error.code || 'Unknown');
        
        reject({
          error: error.message,
          errorCode: error.code,
          time: errorTime,
          connectionAttempted
        });
      });
      
    } catch (err) {
      console.log('❌ Failed to create WebSocket:', err.message);
      reject({
        error: err.message,
        time: 0,
        connectionAttempted: false
      });
    }
  });
}

// Main test execution
async function main() {
  try {
    console.log('🔄 Starting WebSocket connection test...\n');
    
    const result = await testWebSocketConnection();
    
    console.log('\n✅ TEST RESULTS:');
    console.log('================');
    console.log(`Connection successful: ${result.success}`);
    console.log(`Total duration: ${result.connectionTime}ms`);
    console.log(`Messages received: ${result.messagesReceived}`);
    console.log(`Close code: ${result.closeCode}`);
    if (result.closeReason) {
      console.log(`Close reason: ${result.closeReason}`);
    }
    
    if (result.success) {
      console.log('\n🎉 WebSocket URL is accessible and working!');
      console.log('   The issue is likely in the React useEffect implementation.');
    } else {
      console.log('\n⚠️  WebSocket connected but may have issues');
    }
    
  } catch (error) {
    console.log('\n❌ TEST FAILED:');
    console.log('===============');
    console.log(`Error: ${error.error}`);
    console.log(`Time: ${error.time}ms`);
    console.log(`Connection attempted: ${error.connectionAttempted}`);
    
    if (error.errorCode) {
      console.log(`Error code: ${error.errorCode}`);
    }
    
    console.log('\n🔍 ANALYSIS:');
    if (error.error.includes('ENOTFOUND')) {
      console.log('   DNS resolution failed - WebSocket URL may be incorrect');
    } else if (error.error.includes('ECONNREFUSED')) {
      console.log('   Connection refused - WebSocket server may be down');
    } else if (error.error.includes('timeout')) {
      console.log('   Connection timeout - Server may be slow or overloaded');
    } else {
      console.log('   Unknown connection error - Check network and server status');
    }
    
    console.log('\n💡 RECOMMENDATIONS:');
    console.log('   1. Verify the WebSocket URL is correct');
    console.log('   2. Check if the AWS API Gateway WebSocket is deployed');
    console.log('   3. Verify AWS region and stage settings');
    console.log('   4. Test from AWS Console if possible');
    
    process.exit(1);
  }
}

// Handle script termination
process.on('SIGINT', () => {
  console.log('\n\n⏹️  Test interrupted by user');
  process.exit(0);
});

main();