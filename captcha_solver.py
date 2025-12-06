from twocaptcha import TwoCaptcha

def solve_captcha(api_key, site_key, url):
    try:
        solver = TwoCaptcha(api_key)
        result = solver.recaptcha(sitekey=site_key, url=url)
        return result['code']
    except Exception as e:
        print(f"Error solving CAPTCHA: {e}")
        return None
