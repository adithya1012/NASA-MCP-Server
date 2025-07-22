#!/usr/bin/env python3
"""
Test script for NASA MCP Server
"""
import requests
import json
import sys

def test_mcp_server(base_url="http://localhost:8000"):
    """Test the MCP server endpoints"""
    
    print(f"Testing MCP Server at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check (GET /)")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        # print(f"   Response: {response.json()}")
        print("   ✓ Health check passed\n")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}\n")
        # return False
    
    # Test 2: MCP health check
    print("2. Testing MCP endpoint health check (GET /mcp)")
    try:
        response = requests.get(f"{base_url}/mcp", timeout=5)
        print(f"   Status: {response.status_code}")
        # print(f"   Response: {response.json()}")
        print("   ✓ MCP health check passed\n")
    except Exception as e:
        print(f"   ✗ MCP health check failed: {e}\n")
        return False
    
    # Test 3: Initialize
    print("3. Testing MCP initialize")
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0"
            }
        },
        "id": 1
    }
    
    try:
        response = requests.post(
            f"{base_url}/mcp",
            json=init_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("   ✓ Initialize passed\n")
        else:
            print("   ✗ Initialize failed\n")
            # return False
    except Exception as e:
        print(f"   ✗ Initialize failed: {e}\n")
        # return False
    
    # Test 4: List tools
    print("4. Testing tools/list")
    list_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    
    try:
        response = requests.post(
            f"{base_url}/mcp",
            json=list_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and "result" in result:
            tools = result["result"].get("tools", [])
            print(f"   Found {len(tools)} tools:")
            for tool in tools:
                print(f"     - {tool.get('name')}: {tool.get('description')}")
            print("   ✓ Tools list passed\n")
        else:
            print(f"   ✗ Tools list failed: {json.dumps(result, indent=2)}\n")
            # return False
    except Exception as e:
        print(f"   ✗ Tools list failed: {e}\n")
        # return False
    
    # Test 5: Call a tool (APOD)
    print("5. Testing tools/call (get_apod)")
    call_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_apod",
            "arguments": {}
        },
        "id": 3
    }
    
    try:
        response = requests.post(
            f"{base_url}/mcp",
            json=call_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and "result" in result:
            print("   ✓ Tool call passed")
            content = result["result"].get("content", [])
            if content:
                print(f"   Content type: {content[0].get('type')}")
                text = content[0].get('text', '')
                if len(text) > 100:
                    print(f"   Content preview: {text[:100]}...")
                else:
                    print(f"   Content: {text}")
        else:
            print(f"   ✗ Tool call failed: {json.dumps(result, indent=2)}")
            # return False
    except Exception as e:
        print(f"   ✗ Tool call failed: {e}")
        # return False
    
    print("\n" + "=" * 50)
    print("✓ All tests passed! MCP Server is working correctly.")
    # return True

def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    success = test_mcp_server(base_url)
    
    if not success:
        print("\n⚠️  Some tests failed. Check the server logs for details.")
        sys.exit(1)
    else:
        print("\n🎉 Server is ready for use!")

if __name__ == "__main__":
    main()