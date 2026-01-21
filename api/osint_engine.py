"""
OSINT (Open Source Intelligence) Engine for White Beat
Gather public information from various sources
"""

import requests
import json
import logging
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re

logger = logging.getLogger(__name__)


class OSINTEngine:
    """
    OSINT Engine for gathering public intelligence
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_username(self, username):
        """
        Search for username across multiple platforms
        
        Returns:
            Dictionary with platform availability
        """
        platforms = {
            'github': f'https://github.com/{username}',
            'twitter': f'https://twitter.com/{username}',
            'instagram': f'https://instagram.com/{username}',
            'reddit': f'https://reddit.com/user/{username}',
            'linkedin': f'https://linkedin.com/in/{username}',
            'medium': f'https://medium.com/@{username}',
            'dev.to': f'https://dev.to/{username}',
            'stackoverflow': f'https://stackoverflow.com/users/{username}',
        }
        
        results = {}
        
        for platform, url in platforms.items():
            try:
                response = self.session.get(url, timeout=5, allow_redirects=True)
                
                # Check if profile exists
                if response.status_code == 200:
                    results[platform] = {
                        'exists': True,
                        'url': url,
                        'status': 'Found'
                    }
                else:
                    results[platform] = {
                        'exists': False,
                        'url': url,
                        'status': 'Not Found'
                    }
                    
            except Exception as e:
                results[platform] = {
                    'exists': False,
                    'url': url,
                    'status': f'Error: {str(e)}'
                }
        
        return results
    
    def search_email(self, email):
        """
        Search for email information
        
        Returns:
            Email validation and breach check
        """
        result = {
            'email': email,
            'valid_format': self._validate_email_format(email),
            'domain': email.split('@')[1] if '@' in email else None,
        }
        
        # Check if email domain exists
        if result['domain']:
            try:
                import dns.resolver
                dns.resolver.resolve(result['domain'], 'MX')
                result['domain_exists'] = True
            except:
                result['domain_exists'] = False
        
        return result
    
    def search_phone(self, phone):
        """
        Search for phone number information
        
        Returns:
            Phone number details
        """
        # Remove non-numeric characters
        clean_phone = re.sub(r'\D', '', phone)
        
        result = {
            'phone': phone,
            'clean_phone': clean_phone,
            'length': len(clean_phone),
            'valid': len(clean_phone) >= 10,
        }
        
        # Detect country code
        if clean_phone.startswith('91') and len(clean_phone) == 12:
            result['country'] = 'India'
            result['country_code'] = '+91'
        elif clean_phone.startswith('1') and len(clean_phone) == 11:
            result['country'] = 'USA/Canada'
            result['country_code'] = '+1'
        elif clean_phone.startswith('44') and len(clean_phone) == 12:
            result['country'] = 'UK'
            result['country_code'] = '+44'
        
        return result
    
    def search_ip(self, ip_address):
        """
        Get IP address information
        
        Returns:
            IP geolocation and details
        """
        try:
            # Use free IP API
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'ip': ip_address,
                    'country': data.get('country'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'zip': data.get('zip'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'as': data.get('as'),
                }
            else:
                return {'error': 'Failed to fetch IP info'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def search_domain(self, domain):
        """
        Get domain information
        
        Returns:
            Domain details and DNS records
        """
        result = {
            'domain': domain,
            'accessible': False,
            'dns_records': {}
        }
        
        # Check if domain is accessible
        try:
            response = requests.get(f'http://{domain}', timeout=5)
            result['accessible'] = response.status_code == 200
            result['status_code'] = response.status_code
        except:
            result['accessible'] = False
        
        # Get DNS records
        try:
            import dns.resolver
            
            # A records
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                result['dns_records']['A'] = [str(r) for r in a_records]
            except:
                pass
            
            # MX records
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                result['dns_records']['MX'] = [str(r) for r in mx_records]
            except:
                pass
            
            # NS records
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                result['dns_records']['NS'] = [str(r) for r in ns_records]
            except:
                pass
                
        except Exception as e:
            result['dns_error'] = str(e)
        
        return result
    
    def search_github_user(self, username):
        """
        Get detailed GitHub user information
        
        Returns:
            GitHub profile details
        """
        try:
            # GitHub API (no auth required for public data)
            response = requests.get(
                f'https://api.github.com/users/{username}',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'username': data.get('login'),
                    'name': data.get('name'),
                    'bio': data.get('bio'),
                    'company': data.get('company'),
                    'location': data.get('location'),
                    'email': data.get('email'),
                    'blog': data.get('blog'),
                    'twitter': data.get('twitter_username'),
                    'public_repos': data.get('public_repos'),
                    'followers': data.get('followers'),
                    'following': data.get('following'),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'profile_url': data.get('html_url'),
                    'avatar_url': data.get('avatar_url'),
                }
            else:
                return {'error': 'User not found'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def search_social_media(self, query):
        """
        Search across social media platforms
        
        Returns:
            Social media search results
        """
        results = {
            'query': query,
            'platforms': {}
        }
        
        # Twitter search (public)
        try:
            twitter_url = f'https://twitter.com/search?q={quote_plus(query)}'
            results['platforms']['twitter'] = {
                'search_url': twitter_url,
                'status': 'Search available'
            }
        except:
            pass
        
        # Reddit search
        try:
            reddit_url = f'https://www.reddit.com/search/?q={quote_plus(query)}'
            results['platforms']['reddit'] = {
                'search_url': reddit_url,
                'status': 'Search available'
            }
        except:
            pass
        
        return results
    
    def _validate_email_format(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def comprehensive_search(self, query, search_type='auto'):
        """
        Comprehensive OSINT search
        
        Args:
            query: Search query (username, email, IP, domain, etc.)
            search_type: Type of search (auto, username, email, ip, domain)
        
        Returns:
            Comprehensive search results
        """
        results = {
            'query': query,
            'type': search_type,
            'results': {}
        }
        
        # Auto-detect type
        if search_type == 'auto':
            if '@' in query:
                search_type = 'email'
            elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', query):
                search_type = 'ip'
            elif '.' in query and not '@' in query:
                search_type = 'domain'
            else:
                search_type = 'username'
        
        results['detected_type'] = search_type
        
        # Perform appropriate search
        if search_type == 'username':
            results['results']['username_search'] = self.search_username(query)
            results['results']['github'] = self.search_github_user(query)
        elif search_type == 'email':
            results['results']['email_info'] = self.search_email(query)
        elif search_type == 'ip':
            results['results']['ip_info'] = self.search_ip(query)
        elif search_type == 'domain':
            results['results']['domain_info'] = self.search_domain(query)
        
        return results


# Global OSINT engine instance
osint_engine = None

def get_osint_engine():
    """Get or create OSINT engine instance"""
    global osint_engine
    
    if osint_engine is None:
        osint_engine = OSINTEngine()
    
    return osint_engine


def osint_search(query, search_type='auto'):
    """
    Main OSINT search function - use this in views
    
    Args:
        query: Search query
        search_type: Type of search
    
    Returns:
        OSINT results
    """
    engine = get_osint_engine()
    return engine.comprehensive_search(query, search_type)


# Quick test
if __name__ == "__main__":
    print("🧪 Testing OSINT Engine...")
    
    engine = OSINTEngine()
    
    # Test username search
    print("\n1️⃣ Testing username search:")
    result = engine.search_username("torvalds")
    print(json.dumps(result, indent=2))
    
    # Test GitHub search
    print("\n2️⃣ Testing GitHub search:")
    result = engine.search_github_user("torvalds")
    print(json.dumps(result, indent=2))
    
    # Test IP search
    print("\n3️⃣ Testing IP search:")
    result = engine.search_ip("8.8.8.8")
    print(json.dumps(result, indent=2))
