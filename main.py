import discord
from discord import Embed
import asyncio
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.all()

client = commands.Bot(command_prefix='.', intents=intents)

def scrape(word: str):
    try:
        tlds = [
            "com", "xyz", "vip", "app", "bot", "io", "pro", "org", "net", "homes",
            "tech", "info", "page", "dev", "art", "ai", "lol", "wtf", "fun", "biz",
            "space", "cloud", "tech", "host", "online", "website", "site", "meme"
        ]
        
        dots = set(tlds)
        result = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-sh-usage")
        driver = webdriver.Chrome(options=options)
        link = "https://www.namecheap.com/domains/registration/results/?domain=" + word
        driver.get(link)
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        waitlabel = WebDriverWait(driver, 4.5)
        beast_mode = wait.until(EC.element_to_be_clickable((By.ID, "beast-tab-button")))
        beast_mode.click()
        search_box = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="beast-filters"]/div/div/input'))
        )
        for dot in dots:
            search_box.clear()
            search_box.send_keys(dot)
            button_section = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="beast-filters"]/div/dl/dd/ul')
                )
            )
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.text == dot:
                    button.click()
                    break

        generate = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="react-nc-search"]/div/section/div/form/button')
            )
        )
        generate.click()

        results = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="results-wrapper"]'))
        )

        articles = results.find_elements(By.TAG_NAME, "article")
        spans = wait.until(
            EC.visibility_of_all_elements_located(
                (By.XPATH, '//*[@id="results-wrapper"]/article/div[1]/span')
            )
        )

        i = 0
        time.sleep(10)
        while True:
            try:
                namediv = wait.until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="results-wrapper"]/article[' + str(i + 1) + "]/div[1]",
                        )
                    )
                )
                try:
                    span = waitlabel.until(
                        EC.visibility_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="results-wrapper"]/article['
                                + str(i + 1)
                                + "]/div[1]/span",
                            )
                        )
                    )
                    label = span.text
                except:
                    label = "AVAILABLE"
                i += 1
                name = namediv.find_element(By.TAG_NAME, "h2")
                if label == "TAKEN":
                    result.append(name.text)
            except:
                break
        driver.quit()
        result_tlds = [domain.split(".")[-1] for domain in result]
        filtered_result = [domain for domain, tld in zip(result, result_tlds) if tld in tlds]
        return filtered_result

    except Exception as e:
        print(e)
        driver.quit()
        return []


async def function_one(param):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, scrape, param)
    return result


@client.command()
async def search(ctx, *params):
    if params:
        hehe = await ctx.send("**Searching...**")
        tasks = [function_one(param) for param in params]
        results = await asyncio.gather(*tasks) # list of list
        if results:
            for i, result in enumerate(results):
                if result:
                    embed = Embed(
                        title=f"Results for {params[i]}",
                        color=discord.Color.green(),
                        description='\n'.join([f"[{link}](https://{link})" for link in result])
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"**No results found for {params[i]}**")

        await hehe.delete()
    else:
        await ctx.send("**Please provide at least one parameter.**")



client.run(TOKEN)
