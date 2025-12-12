from twocaptcha import TwoCaptcha

def solve_captcha(api_key, site_key, url):
    config = {
        'apiKey': api_key,
        'googlekey': site_key,
        'pageurl': url
    }
    solver = TwoCaptcha(**config)
    try:
        result = solver.recaptcha()
        return result['code']
    except Exception as e:
        print(f"Error solving captcha: {e}")
        return None
