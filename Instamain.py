#!/usr/bin/env python3
"""
InstaRecon - Instagram OSINT Tool
Cyberpunk Edition - Enhanced for Kali Linux & Ethical Hacking
"""

import argparse
import requests
import sys
import subprocess
from urllib.parse import quote_plus
from json import dumps, decoder
import os
import time

# Color codes for cyberpunk theme
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_cyber(text, color=Colors.CYAN):
    print(f"{color}{text}{Colors.RESET}")

def install_dependencies():
    """Install required dependencies"""
    print_cyber("📦 Installing required dependencies...", Colors.YELLOW)
    deps = ["requests", "phonenumbers", "pycountry"]
    
    for dep in deps:
        try:
            print(f"  Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print_cyber(f"❌ Failed to install {dep}", Colors.RED)
            return False
    
    print_cyber("✅ Dependencies installed successfully!\n", Colors.GREEN)
    return True

# Try to import dependencies, install if missing
try:
    import phonenumbers
    from phonenumbers.phonenumberutil import (
        region_code_for_country_code,
        region_code_for_number,
    )
    import pycountry
except ImportError:
    print_cyber("📦 Missing dependencies detected. Installing...", Colors.YELLOW)
    if install_dependencies():
        import phonenumbers
        from phonenumbers.phonenumberutil import (
            region_code_for_country_code,
            region_code_for_number,
        )
        import pycountry
    else:
        print_cyber("❌ Failed to install dependencies. Please install manually:", Colors.RED)
        print("pip install requests phonenumbers pycountry")
        sys.exit(1)


class InstaRecon:
    def __init__(self, session_id, delay=1):
        self.session_id = session_id
        self.delay = delay  # Rate limit avoidance
        self.headers = {
            "User-Agent": "Instagram 64.0.0.14.96",
            "Accept-Language": "en-US",
        }
        self.cookies = {'sessionid': self.session_id}

    def _rate_limit_sleep(self):
        """Small delay to avoid rate limiting"""
        time.sleep(self.delay)

    def get_user_id(self, username):
        """Get user ID from username"""
        headers = {"User-Agent": "iphone_ua", "x-ig-app-id": "936619743392459"}
        
        try:
            self._rate_limit_sleep()
            response = requests.get(
                f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}',
                headers=headers,
                cookies=self.cookies,
                timeout=15
            )
            
            if response.status_code == 404:
                return {"id": None, "error": "User not found"}
            
            if response.status_code == 429:
                return {"id": None, "error": "Rate limit - wait 5-10 minutes"}
            
            data = response.json()
            if 'data' not in data or 'user' not in data['data']:
                return {"id": None, "error": "Invalid response format"}
                
            user_id = data["data"]['user']['id']
            return {"id": user_id, "error": None}
            
        except decoder.JSONDecodeError:
            return {"id": None, "error": "Rate limit - please wait before trying again"}
        except requests.exceptions.Timeout:
            return {"id": None, "error": "Request timeout - please try again"}
        except Exception as e:
            return {"id": None, "error": f"Error: {str(e)}"}

    def get_user_info(self, search, search_type="username"):
        """Get detailed user information"""
        if search_type == "username":
            user_data = self.get_user_id(search)
            if user_data["error"]:
                return {"user": None, "error": user_data["error"]}
            user_id = user_data["id"]
        else:
            try:
                user_id = str(int(search))
            except ValueError:
                return {"user": None, "error": "Invalid ID format"}

        try:
            self._rate_limit_sleep()
            response = requests.get(
                f'https://i.instagram.com/api/v1/users/{user_id}/info/',
                headers=self.headers,
                cookies=self.cookies,
                timeout=15
            )
            
            if response.status_code == 429:
                return {"user": None, "error": "Rate limit - please wait 5-10 minutes before trying again"}
            
            response.raise_for_status()
            
            info_user = response.json().get("user")
            if not info_user:
                return {"user": None, "error": "User not found"}
            
            info_user["userID"] = user_id
            return {"user": info_user, "error": None}
            
        except requests.exceptions.Timeout:
            return {"user": None, "error": "Request timeout - please try again"}
        except requests.exceptions.RequestException as e:
            return {"user": None, "error": f"Request failed: {str(e)}"}

    def advanced_lookup(self, username):
        """Get obfuscated login information"""
        data = "signed_body=SIGNATURE." + quote_plus(dumps(
            {"q": username, "skip_recovery": "1"},
            separators=(",", ":")
        ))
        
        headers = {
            "Accept-Language": "en-US",
            "User-Agent": "Instagram 101.0.0.15.120",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-IG-App-ID": "124024574287414",
            "Accept-Encoding": "gzip, deflate",
            "Host": "i.instagram.com",
            "Connection": "keep-alive",
            "Content-Length": str(len(data))
        }
        
        try:
            self._rate_limit_sleep()
            response = requests.post(
                'https://i.instagram.com/api/v1/users/lookup/',
                headers=headers,
                data=data,
                timeout=15
            )
            return {"user": response.json(), "error": None}
        except decoder.JSONDecodeError:
            return {"user": None, "error": "rate limit"}
        except requests.exceptions.Timeout:
            return {"user": None, "error": "timeout"}

    def format_phone_number(self, country_code, phone_number):
        """Format phone number with country information"""
        phonenr = f"+{country_code} {phone_number}"
        try:
            pn = phonenumbers.parse(phonenr)
            countrycode = region_code_for_country_code(pn.country_code)
            country = pycountry.countries.get(alpha_2=countrycode)
            if country:
                phonenr = f"{phonenr} ({country.name})"
        except:
            pass
        return phonenr

    def safe_get(self, data, key, default="N/A"):
        """Safely get a value from dictionary"""
        return data.get(key, default)

    def display_banner(self):
        """Display cyberpunk banner"""
        banner = f"""
{Colors.CYAN}┌─────────────────────────────────────────────────────────────────┐{Colors.RESET}
{Colors.CYAN}│{Colors.MAGENTA}  ▄ .▄▐▄• ▄ ▄▄▄▄▄            ▄▄▌  .▄▄ ·       ▄▄▄▄▄ ▄▄▄·  ▄▄▄· ▄▄▄▄▄ ▄ .▄  {Colors.CYAN}│{Colors.RESET}
{Colors.CYAN}│{Colors.MAGENTA}  ██▪▐█ █▌█▌▪•██  ▪     ▪     ██•  ▐█ ▀.      •██  ▐█ ▀█ ▐█ ▄█•██  ██▪▐█  {Colors.CYAN}│{Colors.RESET}
{Colors.CYAN}│{Colors.MAGENTA}  ██▀▐█ ·██·  ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  ▄▀▀▀█▄       ▐█.▪▄█▀▀█ ▐█▀▀█ ▐█.▪██▀▐█  {Colors.CYAN}│{Colors.RESET}
{Colors.CYAN}│{Colors.MAGENTA}  ██▌▐▀▪▐█·█▌ ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█▄▪▐█       ▐█▌·▐█ ▪▐▌██▄▪▐█▐█▌·██▌▐▀  {Colors.CYAN}│{Colors.RESET}
{Colors.CYAN}│{Colors.MAGENTA}  ▀▀▀ ·•▀▀ ▀▀ ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀  ▀▀▀▀        ▀▀▀  ▀  ▀ ·▀▀▀▀ ▀▀▀ ▀▀▀   {Colors.CYAN}│{Colors.RESET}
{Colors.CYAN}├─────────────────────────────────────────────────────────────────┤{Colors.RESET}
{Colors.CYAN}│{Colors.YELLOW}                     🔥 CYBERPUNK EDITION 🔥                     {Colors.CYAN}│{Colors.RESET}
{Colors.CYAN}│{Colors.GREEN}                 Instagram OSINT & Security Suite                {Colors.CYAN}│{Colors.RESET}
{Colors.CYAN}│{Colors.BLUE}                     For Ethical Hacking Only                       {Colors.CYAN}│{Colors.RESET}
{Colors.CYAN}└─────────────────────────────────────────────────────────────────┘{Colors.RESET}
        """
        print(banner)

    def display_results(self, info):
        """Display formatted user information"""
        print_cyber("\n" + "="*60, Colors.CYAN)
        print_cyber("INSTAGRAM RECONNAISSANCE RESULTS", Colors.MAGENTA)
        print_cyber("="*60 + "\n", Colors.CYAN)
        
        # Basic Information
        print(f"Username               : {self.safe_get(info, 'username')}")
        print(f"User ID                : {self.safe_get(info, 'userID')}")
        print(f"Full Name              : {self.safe_get(info, 'full_name')}")
        
        # Account Status
        is_verified = self.safe_get(info, 'is_verified', False)
        is_business = self.safe_get(info, 'is_business', False)
        print(f"Verified Account       : {'✅' if is_verified else '❌'}")
        print(f"Business Account       : {'✅' if is_business else '❌'}")
        print(f"Private Account        : {'✅' if self.safe_get(info, 'is_private', False) else '❌'}")
        
        # Statistics
        followers = self.safe_get(info, 'follower_count', 0)
        following = self.safe_get(info, 'following_count', 0)
        posts = self.safe_get(info, 'media_count', 0)
        
        print_cyber(f"\n📊 Engagement Metrics:", Colors.YELLOW)
        print(f"Followers              : {followers:,}")
        print(f"Following              : {following:,}")
        print(f"Posts                  : {posts:,}")
        
        # Calculate engagement ratio if applicable
        if followers > 0:
            ratio = following / followers
            print(f"Following/Follower Ratio: {ratio:.2f}")
        
        # Optional fields
        if info.get("external_url"):
            print_cyber(f"\n🌐 External Links:", Colors.YELLOW)
            print(f"Website                : {info['external_url']}")
        
        # Biography
        if info.get("biography"):
            print_cyber(f"\n📝 Biography:", Colors.YELLOW)
            bio_lines = info["biography"].split("\n")
            for i, line in enumerate(bio_lines):
                if line.strip():
                    prefix = "                       " if i > 0 else ""
                    print(f"{prefix}{line}")
        
        # Contact Information
        contact_found = False
        if info.get("public_email"):
            if not contact_found:
                print_cyber(f"\n📧 Contact Info:", Colors.YELLOW)
                contact_found = True
            print(f"Email                  : {info['public_email']}")
        
        if info.get("public_phone_number"):
            if not contact_found:
                print_cyber(f"\n📞 Contact Info:", Colors.YELLOW)
                contact_found = True
            phone = self.format_phone_number(
                info.get("public_phone_country_code", ""),
                info["public_phone_number"]
            )
            print(f"Phone                  : {phone}")
        
        # Profile Picture
        profile_pic_url = None
        if 'hd_profile_pic_url_info' in info and info['hd_profile_pic_url_info'].get('url'):
            profile_pic_url = info['hd_profile_pic_url_info']['url']
        elif 'profile_pic_url_hd' in info:
            profile_pic_url = info['profile_pic_url_hd']
        elif 'profile_pic_url' in info:
            profile_pic_url = info['profile_pic_url']
        
        if profile_pic_url:
            print_cyber(f"\n🖼️  Profile Picture        : {profile_pic_url}", Colors.BLUE)
        
        # Advanced lookup
        print_cyber("\n" + "─"*60, Colors.CYAN)
        print_cyber("🔍 ADVANCED RECONNAISSANCE", Colors.MAGENTA)
        print_cyber("─"*60, Colors.CYAN)
        
        other_info = self.advanced_lookup(info["username"])
        
        if other_info["error"] == "rate limit":
            print_cyber("⚠️  Rate limit reached - please wait 5-10 minutes", Colors.YELLOW)
        elif other_info["error"] == "timeout":
            print_cyber("⚠️  Request timeout - please try again later", Colors.YELLOW)
        elif other_info["user"] and "message" in other_info["user"]:
            if other_info["user"]["message"] == "No users found":
                print("No additional reconnaissance data available")
            else:
                print(f"Status: {other_info['user']['message']}")
        elif other_info["user"]:
            recon_found = False
            if other_info["user"].get("obfuscated_email"):
                print(f"Obfuscated Email       : {other_info['user']['obfuscated_email']}")
                recon_found = True
            
            if other_info["user"].get("obfuscated_phone"):
                print(f"Obfuscated Phone       : {other_info['user']['obfuscated_phone']}")
                recon_found = True
                
            if not recon_found:
                print("No obfuscated contact information found")
        
        print_cyber("\n" + "="*60, Colors.CYAN)
        
        # Security Note
        print_cyber("\n🔒 Security Note: This information is publicly available", Colors.BLUE)
        print_cyber("   Use responsibly and in accordance with applicable laws.", Colors.BLUE)
        

def main():
    parser = argparse.ArgumentParser(
        description="InstaRecon - Instagram OSINT Tool (Cyberpunk Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CYAN}Examples:{Colors.RESET}
  python instarecon.py -u username -s your_session_id
  python instarecon.py -i 123456789 -s your_session_id
  python instarecon.py -u username -s your_session_id --debug
  python instarecon.py -u username -s your_session_id --delay 2

{Colors.YELLOW}Getting your Instagram session ID:{Colors.RESET}
  1. Open Instagram in your browser and log in
  2. Open Developer Tools (F12)
  3. Go to Application/Storage → Cookies → https://www.instagram.com
  4. Find and copy the 'sessionid' value

{Colors.RED}⚠️  LEGAL DISCLAIMER:{Colors.RESET}
This tool is for educational and authorized penetration testing purposes only.
Users are responsible for complying with applicable laws and regulations.
        """
    )
    
    parser.add_argument('-s', '--sessionid', help="Instagram session ID", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--username', help="Instagram username")
    group.add_argument('-i', '--id', help="Instagram user ID")
    parser.add_argument('--debug', action='store_true', help="Show debug information")
    parser.add_argument('--no-banner', action='store_true', help="Skip banner display")
    parser.add_argument('--delay', type=int, default=2, help="Delay between requests (default: 2 seconds)")
    
    args = parser.parse_args()
    
    # Create InstaRecon instance with delay
    recon = InstaRecon(args.sessionid, delay=args.delay)
    
    # Display banner
    if not args.no_banner:
        recon.display_banner()
    
    print_cyber(f"🔍 Starting reconnaissance for {args.username or args.id}", Colors.YELLOW)
    print_cyber("⏳ Gathering intelligence...\n", Colors.YELLOW)
    
    # Determine search type and value
    search_type = "id" if args.id else "username"
    search_value = args.id or args.username
    
    # Get user information
    result = recon.get_user_info(search_value, search_type)
    
    if result.get("error"):
        print_cyber(f"\n❌ Error: {result['error']}", Colors.RED)
        
        # Provide helpful suggestions
        if "Rate limit" in result['error']:
            print_cyber("\n💡 Try again in 5-10 minutes or use a different session ID", Colors.YELLOW)
            print_cyber("💡 Use --delay 3 to add longer delays between requests", Colors.YELLOW)
        elif "User not found" in result['error']:
            print_cyber("\n💡 Check the username/ID spelling and try again", Colors.YELLOW)
        elif "timeout" in result['error'].lower():
            print_cyber("\n💡 Check your internet connection and try again", Colors.YELLOW)
            
        sys.exit(1)
    
    # Display results
    recon.display_results(result["user"])
    
    # Debug information
    if args.debug:
        print_cyber("\n" + "─"*60, Colors.CYAN)
        print_cyber("DEBUG INFORMATION", Colors.MAGENTA)
        print_cyber("─"*60, Colors.CYAN)
        print("\nAll available fields:")
        for key, value in result["user"].items():
            if not key.endswith('_url'):  # Skip URLs for cleaner output
                print(f"  {key}: {value}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_cyber("\n\n⚠️  Operation cancelled by user", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_cyber(f"\n❌ Unexpected error: {str(e)}", Colors.RED)
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        else:
            print_cyber("💡 Run with --debug flag for detailed error information", Colors.YELLOW)
        sys.exit(1)
