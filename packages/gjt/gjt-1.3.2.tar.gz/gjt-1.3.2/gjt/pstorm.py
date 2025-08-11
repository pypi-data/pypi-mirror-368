import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .just_funcs import getserver
import json as json_module
import re
class RecaptchaTokenGenerator:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1)

    def _generate_recaptcha_token_sync(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--log-level=3")
            options.add_argument("--no-sandbox")
            options.add_argument("--window-size=1,1")
            options.add_argument("--headless=new")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            driver = webdriver.Chrome(options=options)

            driver.get("https://empire.goodgamestudios.com/")
            wait = WebDriverWait(driver, 30, poll_frequency=0.01)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe#game')))
            iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#game')
            driver.switch_to.frame(iframe)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.grecaptcha-badge')))

            result = driver.execute_script("""
                return new Promise((resolve) => {
                    window.grecaptcha.ready(() => {
                        window.grecaptcha.execute('6Lc7w34oAAAAAFKhfmln41m96VQm4MNqEdpCYm-k', { action: 'submit' }).then(resolve);
                    });
                });
            """)

            driver.quit()
            return result
        except Exception as e:
            raise e

    async def generate_recaptcha_token(self):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._generate_recaptcha_token_sync)

async def ggs_login(ws, nick: str, pwrd: str, server: str, kid: int | None = 0) -> tuple:
    
    """
    Login to your account and return the coordinates of your main castle.
    """
    server = getserver(server, "ex")
    generator = RecaptchaTokenGenerator()
    token = await generator.generate_recaptcha_token()
    if ws.open:
        await ws.send(f"""<msg t='sys'><body action='verChk' r='0'><ver v='166' /></body></msg>""")
        await ws.send(f"""<msg t='sys'><body action='login' r='0'><login z='{server}'><nick><![CDATA[]]></nick><pword><![CDATA[605015%pl%0]]></pword></login></body></msg>""")
        await ws.send(f"""<msg t='sys'><body action='autoJoin' r='-1'></body></msg>""")
        await ws.send(f"""<msg t='sys'><body action='roundTrip' r='1'></body></msg>""")
        await ws.send(f"""%xt%{server}%vln%1%{{"NOM": "{nick}"}}%""")
        await ws.send(f"""%xt%{server}%lli%1%{{"CONM":1752,"RTM":24,"ID":0,"PL":1,"NOM":"{nick}","PW":"{pwrd}","LT":null,"LANG":"pl","DID":"0","AID":"1748087142659830366","KID":"","REF":"https://empire.goodgamestudios.com","GCI":"","SID":9,"PLFID":1,"RCT":"{token}"}}%""")
        while ws.open:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=7.5)
                response = response.decode('utf-8')

                if "%xt%lli%1%" in response:
                    if "%xt%lli%1%0%" not in response:
                        print("Wrong login data.")
                        exit()
                elif "%xt%gbd%1%0%" in response:
                    response = response.replace('%xt%gbd%1%0%', '').rstrip('%').strip()
                    response = json_module.loads(response)
                    lids = []
                    fragments = response["gli"]["C"]
                    for fragment in fragments:
                        lids.append(fragment["ID"])
                    lids = sorted(lids)
                    break
            except asyncio.TimeoutError:
                break
        await ws.send(f"%xt%{server}%nch%1%")
        await ws.send(f"""%xt%{server}%core_gic%1%{{"T":"link","CC":"PL","RR":"html5"}}%""")
        await ws.send(f"%xt%{server}%gbl%1%{{}}%")
        await ws.send(f"""%xt%{server}%jca%1%{{"CID":-1,"KID":0}}%""")
        await ws.send(f"%xt%{server}%alb%1%{{}}%")
        await ws.send(f"%xt%{server}%sli%1%{{}}%")
        await ws.send(f"%xt%{server}%gie%1%{{}}%")
        await ws.send(f"%xt%{server}%asc%1%{{}}%")
        await ws.send(f"%xt%{server}%sie%1%{{}}%")
        await ws.send(f"""%xt%{server}%ffi%1%{{"FIDS":[1]}}%""")
        await ws.send(f"%xt%{server}%kli%1%{{}}%")
        while ws.open:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=6)
                response = response.decode('utf-8')
                if "%xt%jaa%1%0%" in response:
                    sx_list = []
                    sy_list = []
                    cid_list = []
                    for i in range(4):
                        pattern = rf"\[{i},(\d+),(\d+),(\d+),1"
                        match = re.search(pattern, response)
                        if match:
                            cid = match.group(1)
                            sx = match.group(2)
                            sy = match.group(3)
                            sx_list.append(sx)
                            sy_list.append(sy)
                            cid_list.append(cid)
                            print(f"Coord {i} X: {sx}, Coord Y: {sy}")
                    break

            except asyncio.TimeoutError:
                break

        while ws.open:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.5)
                response = response.decode('utf-8')
                if "%xt%ffi%1%0%" in response:
                    await ws.send(f"%xt%{server}%gcs%1%{{}}%")
                    print("Successfully logged in")
                    break
            except asyncio.TimeoutError:
                break
    else:
        print("Connection closed, stopping login")
    return sx_list, sy_list, lids, cid_list