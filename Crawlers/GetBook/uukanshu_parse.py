from requests import Response
import os,io
from bs4 import BeautifulSoup
import threading
import re,time

SITE = "https://www.uukanshu.com/"

def parse_menu(content:Response):
    print(content.text)