#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import time
import random
import logging
import sys
import traceback
import base64
import re
from urllib.parse import urlparse, urljoin, urlunparse
from typing import Optional, Dict, Tuple, Union, List, Set

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("url_fetcher")

# 定义可能使用的渲染方法
RENDER_METHOD_REQUESTS = "requests"  # 简单请求，不执行JS
RENDER_METHOD_PLAYWRIGHT = "playwright"  # 使用Playwright进行完整浏览器渲染
RENDER_METHOD_SELENIUM = "selenium"  # 使用Selenium进行完整浏览器渲染

# 检查是否已安装Playwright
has_playwright = False
try:
    from playwright.sync_api import sync_playwright
    has_playwright = True
    logger.info("已加载Playwright，支持完整浏览器渲染")
except ImportError:
    logger.warning("未检测到Playwright，无法使用完整浏览器渲染。如需使用，请运行: pip install playwright && playwright install chromium")

# 检查是否已安装Selenium
has_selenium = False
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    has_selenium = True
    logger.info("已加载Selenium，支持完整浏览器渲染")
except ImportError:
    logger.warning("未检测到Selenium，无法使用该方法进行浏览器渲染。如需使用，请运行: pip install selenium")

class UrlFetcher:
    """
    URL获取和解析的工具类，负责从网页URL获取HTML内容
    支持多种获取方法：原始请求、Playwright、Selenium
    可以处理内链，输出静态HTML文件
    """
    
    def __init__(self, headers: Optional[Dict[str, str]] = None, timeout: int = 30, 
                 render_method: str = RENDER_METHOD_PLAYWRIGHT, wait_time: int = 5,
                 inline_resources: bool = True, max_resource_size: int = 5*1024*1024,
                 remove_scripts: bool = False, remove_images: bool = False):
        """
        初始化UrlFetcher类
        
        Args:
            headers: 请求头字典，默认为模拟常规浏览器
            timeout: 请求超时时间，默认30秒
            render_method: 渲染方法，可选值: "requests"(仅HTML), "playwright"(默认), "selenium"
            wait_time: 浏览器渲染等待时间(秒)
            inline_resources: 是否内联资源(CSS, JS, 图片等)
            max_resource_size: 最大内联资源大小，默认5MB
            remove_scripts: 是否移除所有script标签，默认False
            remove_images: 是否移除所有图片标签，默认False
        """
        self.timeout = timeout
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        self.render_method = render_method
        self.wait_time = wait_time
        self.inline_resources = inline_resources
        self.max_resource_size = max_resource_size
        self.resource_cache = {}  # 缓存已下载的资源
        self.remove_scripts = remove_scripts
        self.remove_images = remove_images
        
        # 验证渲染方法是否可用
        if self.render_method == RENDER_METHOD_PLAYWRIGHT and not has_playwright:
            logger.warning("Playwright未安装，将回退到requests方法")
            self.render_method = RENDER_METHOD_SELENIUM if has_selenium else RENDER_METHOD_REQUESTS
            
        if self.render_method == RENDER_METHOD_SELENIUM and not has_selenium:
            logger.warning("Selenium未安装，将回退到requests方法")
            self.render_method = RENDER_METHOD_REQUESTS
    
    def _fetch_with_requests(self, url: str) -> Tuple[Union[bytes, None], int]:
        """使用requests库获取URL内容（不执行JavaScript）"""
        try:
            logger.info(f"使用requests获取URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            status_code = response.status_code
            
            if status_code == 200:
                # 使用原始二进制内容，避免编码问题
                html_content = response.content
                return html_content, status_code
            else:
                logger.warning(f"requests获取URL失败: {url}, 状态码: {status_code}")
                return None, status_code
        except requests.RequestException as e:
            logger.error(f"requests请求异常: {url}, 错误: {str(e)}")
            return None, 0
        except Exception as e:
            logger.error(f"requests解析异常: {url}, 错误: {str(e)}")
            return None, 0
    
    def _fetch_with_playwright(self, url: str) -> Tuple[Union[str, None], Union[str, None], int]:
        """使用Playwright获取URL内容（完整浏览器渲染，执行JavaScript）"""
        if not has_playwright:
            logger.error("Playwright未安装，无法使用该方法")
            return None, None, 0
        
        try:
            logger.info(f"使用Playwright获取URL: {url}")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent=self.headers.get("User-Agent")
                )
                
                page = context.new_page()
                
                # 添加额外的请求头
                page.set_extra_http_headers(self.headers)
                
                # 访问页面并等待加载
                response = page.goto(url, timeout=self.timeout * 1000, wait_until="networkidle")
                status_code = response.status if response else 0
                
                if not response or status_code != 200:
                    browser.close()
                    logger.warning(f"Playwright获取URL失败: {url}, 状态码: {status_code}")
                    return None, None, status_code
                
                # 等待页面渲染完成
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(self.wait_time * 1000)  # 额外等待以确保JS执行完毕
                
                # 获取页面标题
                title = page.title()
                
                # 获取渲染后的HTML内容
                html_content = page.content()
                
                # 提取渲染后的文本内容
                text_content = page.evaluate("""() => {
                    return document.body.innerText;
                }""")
                
                # 清理资源
                browser.close()
                
                return html_content, text_content, status_code
        except Exception as e:
            logger.error(f"Playwright获取异常: {url}, 错误: {str(e)}")
            traceback.print_exc()
            return None, None, 0
    
    def _fetch_with_selenium(self, url: str) -> Tuple[Union[str, None], Union[str, None], int]:
        """使用Selenium获取URL内容（完整浏览器渲染，执行JavaScript）"""
        if not has_selenium:
            logger.error("Selenium未安装，无法使用该方法")
            return None, None, 0
        
        driver = None
        try:
            logger.info(f"使用Selenium获取URL: {url}")
            # 配置Chrome选项
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.headers.get('User-Agent')}")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # 启动浏览器
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            
            # 访问页面
            driver.get(url)
            
            # 等待页面加载完成
            time.sleep(self.wait_time)  # 等待JavaScript执行
            
            # 获取页面标题
            title = driver.title
            
            # 获取渲染后的HTML
            html_content = driver.page_source
            
            # 获取文本内容
            text_content = driver.find_element(By.TAG_NAME, "body").text
            
            # 假设成功获取（Selenium不提供状态码）
            return html_content, text_content, 200
        except TimeoutException:
            logger.error(f"Selenium加载超时: {url}")
            return None, None, 408  # 请求超时
        except WebDriverException as e:
            logger.error(f"Selenium浏览器异常: {url}, 错误: {str(e)}")
            return None, None, 0
        except Exception as e:
            logger.error(f"Selenium获取异常: {url}, 错误: {str(e)}")
            traceback.print_exc()
            return None, None, 0
        finally:
            # 清理资源
            if driver:
                driver.quit()

    def _get_resource(self, resource_url: str, base_url: str) -> Tuple[Union[str, None], str, str]:
        """
        获取资源内容并将其转换为Data URL或相对路径
        
        Args:
            resource_url: 资源URL
            base_url: 基础URL，用于解析相对URL
            
        Returns:
            tuple: (资源内容, 内容类型, Data URL或原URL)
        """
        # 检查缓存
        if resource_url in self.resource_cache:
            return self.resource_cache[resource_url]
            
        try:
            # 解析资源URL
            parsed_resource_url = urlparse(resource_url)
            
            # 如果是相对URL，则转换为绝对URL
            if not parsed_resource_url.netloc:
                absolute_url = urljoin(base_url, resource_url)
                parsed_resource_url = urlparse(absolute_url)
            else:
                absolute_url = resource_url
            
            # 跳过data URLs、javascript URLs和锚点
            if (parsed_resource_url.scheme in ['data', 'javascript'] or 
                not parsed_resource_url.netloc or
                resource_url.startswith('#')):
                return None, "", resource_url
            
            # 获取资源内容
            try:
                response = requests.get(
                    absolute_url, 
                    headers=self.headers, 
                    timeout=self.timeout,
                    stream=True  # 使用流式传输，避免一次性加载大文件
                )
                
                # 确保使用UTF-8编码处理文本资源
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    logger.warning(f"获取资源失败: {absolute_url}, 状态码: {response.status_code}")
                    return None, "", resource_url
                
                # 获取内容类型
                content_type = response.headers.get('content-type', '').split(';')[0]
                if not content_type:
                    # 根据URL后缀猜测内容类型
                    extension = os.path.splitext(parsed_resource_url.path)[1].lower()
                    content_type = {
                        '.css': 'text/css',
                        '.js': 'application/javascript',
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.svg': 'image/svg+xml',
                        '.webp': 'image/webp',
                        '.ttf': 'font/ttf',
                        '.woff': 'font/woff',
                        '.woff2': 'font/woff2',
                        '.eot': 'font/eot',
                    }.get(extension, 'application/octet-stream')
                
                # 检查资源大小
                content_length = int(response.headers.get('content-length', 0))
                if content_length and content_length > self.max_resource_size:
                    logger.warning(f"资源过大: {absolute_url}, 大小: {content_length} 字节")
                    return None, content_type, resource_url
                
                # 获取资源内容
                content = response.content
                
                # 再次检查大小（以防content-length不准确）
                if len(content) > self.max_resource_size:
                    logger.warning(f"资源过大: {absolute_url}, 大小: {len(content)} 字节")
                    return None, content_type, resource_url
                
                # 创建Base64编码的Data URL
                data_url = f"data:{content_type};base64,{base64.b64encode(content).decode('utf-8')}"
                
                # 缓存结果
                result = (content, content_type, data_url)
                self.resource_cache[resource_url] = result
                return result
            
            except requests.RequestException as e:
                logger.error(f"请求资源出错: {absolute_url}, 错误: {str(e)}")
                return None, "", resource_url
                
        except Exception as e:
            logger.error(f"处理资源URL出错: {resource_url}, 错误: {str(e)}")
            return None, "", resource_url
    
    def _staticize_html(self, html_content: str, base_url: str) -> str:
        """
        将HTML中的外部资源内联化，转换为完全静态的HTML
        根据配置可以移除所有脚本和图片
        
        Args:
            html_content: HTML内容
            base_url: 基础URL，用于解析相对URL
            
        Returns:
            处理后的HTML内容
        """
        logger.info(f"开始静态化处理HTML内容，基础URL: {base_url}")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            processed_urls = set()  # 记录已处理过的URLs，避免重复处理
            
            # 1. 根据配置移除所有脚本标签
            if self.remove_scripts:
                logger.info("正在移除所有脚本标签...")
                # 移除所有script标签
                scripts_removed = 0
                for script in soup.find_all('script'):
                    script.extract()  # 从DOM中移除元素
                    scripts_removed += 1
                
                # 移除可能包含javascript的元素属性
                js_attrs = ['onclick', 'onload', 'onunload', 'onchange', 'onsubmit', 
                           'onreset', 'onselect', 'onblur', 'onfocus', 'onkeydown', 
                           'onkeypress', 'onkeyup', 'onmouseover', 'onmouseout', 
                           'onmousedown', 'onmouseup', 'onmousemove', 'ondblclick']
                
                attrs_removed = 0
                for attr in js_attrs:
                    for tag in soup.find_all(attrs={attr: True}):
                        del tag[attr]
                        attrs_removed += 1
                
                # 移除带有javascript:的href属性
                js_hrefs_removed = 0
                for a in soup.find_all('a', href=True):
                    if a['href'].startswith('javascript:'):
                        a['href'] = '#'
                        js_hrefs_removed += 1
                
                logger.info(f"已移除 {scripts_removed} 个脚本标签, {attrs_removed} 个事件属性, {js_hrefs_removed} 个javascript链接")
            
            # 2. 根据配置移除所有图片标签
            if self.remove_images:
                logger.info("正在移除所有图片和媒体标签...")
                # 移除所有图片标签
                images_removed = 0
                for img in soup.find_all('img'):
                    img.extract()
                    images_removed += 1
                
                # 移除背景图片样式
                style_attrs_updated = 0
                for tag in soup.find_all(style=True):
                    if 'background' in tag['style'] and ('url(' in tag['style'] or 'image' in tag['style']):
                        # 移除背景图片但保留其他样式
                        style = tag['style']
                        style = re.sub(r'background-image\s*:[^;]+;?', '', style)
                        style = re.sub(r'background\s*:[^;]*url\([^)]+\)[^;]*;?', '', style)
                        tag['style'] = style
                        style_attrs_updated += 1
                
                # 移除其他媒体元素
                media_removed = 0
                for media in soup.find_all(['video', 'audio', 'picture', 'svg', 'canvas', 'iframe']):
                    media.extract()
                    media_removed += 1
                
                logger.info(f"已移除 {images_removed} 个图片, {style_attrs_updated} 个背景图片样式, {media_removed} 个其他媒体元素")
            
            # 3. 内联资源处理（如果启用）
            if self.inline_resources:
                # 处理CSS链接
                for link in soup.find_all('link', rel='stylesheet'):
                    href = link.get('href')
                    if href and href not in processed_urls:
                        processed_urls.add(href)
                        content, content_type, data_url = self._get_resource(href, base_url)
                        if content:
                            # 替换为内联样式
                            style_tag = soup.new_tag('style')
                            style_tag['type'] = 'text/css'
                            style_tag.string = content.decode('utf-8', errors='ignore')
                            link.replace_with(style_tag)
                        elif data_url and data_url.startswith('data:'):
                            # 替换为Data URL
                            link['href'] = data_url
                
                # 处理内联样式中的URL
                for style in soup.find_all('style'):
                    if style.string:
                        # 处理CSS中的url()引用
                        style.string = re.sub(
                            r'url\(["\']?([^"\'()]+)["\']?\)',
                            lambda m: self._process_css_url(m, base_url, processed_urls),
                            style.string
                        )
                
                # 处理元素内联样式中的URL
                for tag in soup.find_all(style=True):
                    style_attr = tag['style']
                    if 'url(' in style_attr:
                        tag['style'] = re.sub(
                            r'url\(["\']?([^"\'()]+)["\']?\)',
                            lambda m: self._process_css_url(m, base_url, processed_urls),
                            style_attr
                        )
                
                # 处理JavaScript（仅当未选择移除所有脚本时）
                if not self.remove_scripts:
                    for script in soup.find_all('script', src=True):
                        src = script.get('src')
                        if src and src not in processed_urls:
                            processed_urls.add(src)
                            content, content_type, data_url = self._get_resource(src, base_url)
                            if content:
                                # 替换为内联脚本
                                script_content = content.decode('utf-8', errors='ignore')
                                del script['src']
                                script.string = script_content
                            elif data_url and data_url.startswith('data:'):
                                # 替换为Data URL
                                script['src'] = data_url
                
                # 处理图片（仅当未选择移除所有图片时）
                if not self.remove_images:
                    for img in soup.find_all('img', src=True):
                        src = img.get('src')
                        if src and src not in processed_urls:
                            processed_urls.add(src)
                            content, content_type, data_url = self._get_resource(src, base_url)
                            if data_url and data_url.startswith('data:'):
                                img['src'] = data_url
                
                # 处理视频和音频源（如果允许保留媒体）
                if not self.remove_images:
                    for media in soup.find_all(['video', 'audio']):
                        for source in media.find_all('source', src=True):
                            src = source.get('src')
                            if src and src not in processed_urls:
                                processed_urls.add(src)
                                content, content_type, data_url = self._get_resource(src, base_url)
                                if data_url and data_url.startswith('data:'):
                                    source['src'] = data_url
            
            # 处理链接，使所有链接为绝对URL
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href and not href.startswith(('javascript:', '#', 'data:', 'mailto:', 'tel:')):
                    # 转换相对URL为绝对URL
                    a['href'] = urljoin(base_url, href)
            
            # 处理表单action
            for form in soup.find_all('form', action=True):
                action = form.get('action')
                if action and not action.startswith(('javascript:', '#', 'data:')):
                    form['action'] = urljoin(base_url, action)
            
            # 添加base标签，确保所有相对URL基于正确的基础URL
            head = soup.head or soup.html.insert(0, soup.new_tag('head'))
            existing_base = soup.find('base')
            if existing_base:
                existing_base['href'] = base_url
            else:
                base_tag = soup.new_tag('base')
                base_tag['href'] = base_url
                head.insert(0, base_tag)
            
            # 添加元信息标记，表明这是静态处理后的页面
            meta_tag = soup.new_tag('meta')
            meta_tag['name'] = 'static-page-generator'
            meta_tag['content'] = 'UrlFetcher'
            head.append(meta_tag)
            
            logger.info(f"HTML静态化处理完成，共处理 {len(processed_urls)} 个资源")
            return str(soup)
            
        except Exception as e:
            logger.error(f"静态化HTML出错: {str(e)}")
            traceback.print_exc()
            # 出错时返回原始HTML
            return html_content
    
    def _process_css_url(self, match, base_url: str, processed_urls: Set[str]) -> str:
        """处理CSS中的url()引用"""
        url = match.group(1)
        if url in processed_urls or url.startswith(('data:', 'javascript:', '#')):
            return f'url("{url}")'
        
        processed_urls.add(url)
        content, content_type, data_url = self._get_resource(url, base_url)
        if data_url and data_url.startswith('data:'):
            return f'url("{data_url}")'
        return f'url("{url}")'
    
    def fetch_url(self, url: str) -> Tuple[Union[bytes, None], Union[str, None], Union[str, None], int]:
        """
        获取URL的HTML内容和渲染后的文本，并处理内链使其完全静态化
        
        Args:
            url: 需要获取的URL
            
        Returns:
            tuple: (静态化HTML内容(二进制), 文本内容, 页面标题, 状态码)
                如果获取失败，HTML内容为None
        """
        try:
            logger.info(f"正在获取URL: {url}，使用渲染方法: {self.render_method}")
            
            # 根据渲染方法选择不同的获取方式
            if self.render_method == RENDER_METHOD_PLAYWRIGHT:
                html_content, text_content, status_code = self._fetch_with_playwright(url)
                
                # 使用BeautifulSoup提取标题
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    title_tag = soup.find('title')
                    title = title_tag.text if title_tag else url
                else:
                    title = url
                    
            elif self.render_method == RENDER_METHOD_SELENIUM:
                html_content, text_content, status_code = self._fetch_with_selenium(url)
                
                # 使用BeautifulSoup提取标题
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    title_tag = soup.find('title')
                    title = title_tag.text if title_tag else url
                else:
                    title = url
                    
            else:  # 默认使用requests
                html_content, status_code = self._fetch_with_requests(url)
                
                # 使用BeautifulSoup提取标题和文本
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    title_tag = soup.find('title')
                    title = title_tag.text if title_tag else url
                    # 提取文本内容
                    text_content = soup.get_text(separator='\n', strip=True)
                else:
                    title = url
                    text_content = None
            
            # 如果获取失败
            if html_content is None:
                logger.warning(f"获取URL失败: {url}, 状态码: {status_code}")
                return None, None, url, status_code
            
            # 对于二进制内容，直接返回不进行静态转换
            # 检查是否为二进制数据
            if isinstance(html_content, bytes):
                try:
                    # 尝试检测编码
                    import chardet
                    detected = chardet.detect(html_content)
                    logger.info(f"检测到内容编码: {detected}")
                    
                    # 如果像是二进制文件而非文本，直接返回二进制内容
                    if detected['encoding'] is None or detected['confidence'] < 0.5:
                        logger.info(f"检测到可能是二进制文件，直接返回二进制内容")
                        return html_content, text_content, title, status_code
                    
                    # 尝试解码为文本以进行静态处理
                    text_html = html_content.decode(detected['encoding'], errors='replace')
                    static_html = self._staticize_html(text_html, url)
                    # 再转回二进制
                    return static_html.encode(detected['encoding'], errors='replace'), text_content, title, status_code
                except Exception as e:
                    logger.warning(f"编码处理失败，返回原始二进制数据: {str(e)}")
                    return html_content, text_content, title, status_code
            else:
                # 处理文本内容
                static_html = self._staticize_html(html_content, url)
                logger.info(f"成功获取URL: {url}, 标题: {title}")
                return static_html, text_content, title, status_code
            
        except Exception as e:
            logger.error(f"获取URL时出错: {url}, 错误: {str(e)}")
            traceback.print_exc()
            return None, None, url, 0
    
    def save_html_to_file(self, html_content: Union[str, bytes], output_path: Union[str, Path]) -> Path:
        """
        将HTML内容保存到文件
        
        Args:
            html_content: HTML内容(字符串或二进制)
            output_path: 保存文件的路径
            
        Returns:
            保存的文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 根据内容类型选择正确的保存方式
        if isinstance(html_content, bytes):
            # 二进制内容
            with open(output_path, 'wb') as f:
                f.write(html_content)
        else:
            # 文本内容
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            except UnicodeEncodeError:
                # 如果编码失败，尝试以二进制方式写入
                with open(output_path, 'wb') as f:
                    f.write(html_content.encode('utf-8', errors='replace'))
        
        logger.info(f"内容已保存到: {output_path}")
        return output_path
        
    def save_text_to_file(self, text_content: Union[str, bytes, None], output_path: Union[str, Path]) -> Path:
        """
        将文本内容保存到文件
        
        Args:
            text_content: 文本内容(字符串、二进制或None)
            output_path: 保存文件的路径
            
        Returns:
            保存的文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果内容为空
        if text_content is None:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("无法提取文本内容")
            return output_path
            
        # 处理不同类型的内容
        if isinstance(text_content, bytes):
            try:
                # 尝试检测编码
                import chardet
                detected = chardet.detect(text_content)
                if detected['encoding'] is None:
                    # 二进制文件，直接保存
                    with open(output_path, 'wb') as f:
                        f.write(text_content)
                else:
                    # 尝试解码文本
                    with open(output_path, 'w', encoding=detected['encoding'], errors='replace') as f:
                        f.write(text_content.decode(detected['encoding'], errors='replace'))
            except Exception:
                # 如果解码失败，直接以二进制方式保存
                with open(output_path, 'wb') as f:
                    f.write(text_content)
        else:
            # 文本内容
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
        
        logger.info(f"文本内容已保存到: {output_path}")
        return output_path

def fetch_and_save_url(url: str, output_dir: Union[str, Path], 
                       filename: Optional[str] = None, 
                       render_method: str = RENDER_METHOD_PLAYWRIGHT,
                       wait_time: int = 5,
                       inline_resources: bool = True) -> Tuple[Union[Dict, None], str, int]:
    """
    获取URL内容并保存为静态HTML和文本文件
    
    Args:
        url: 要获取的URL
        output_dir: 输出目录
        filename: 保存的文件名，如果不提供则基于URL自动生成
        render_method: 渲染方法，可选值: "requests", "playwright", "selenium"
        wait_time: 浏览器渲染等待时间(秒)
        inline_resources: 是否内联资源(CSS, JS, 图片等)
        
    Returns:
        tuple: (保存的文件信息字典, 页面标题, 状态码)
            如果获取失败，返回(None, 标题, 状态码)
    """
    # 选择合适的渲染方法
    if render_method == RENDER_METHOD_PLAYWRIGHT and not has_playwright:
        logger.warning("Playwright未安装，回退到Selenium")
        render_method = RENDER_METHOD_SELENIUM if has_selenium else RENDER_METHOD_REQUESTS
    
    if render_method == RENDER_METHOD_SELENIUM and not has_selenium:
        logger.warning("Selenium未安装，回退到requests")
        render_method = RENDER_METHOD_REQUESTS
    
    # 创建URL获取器
    fetcher = UrlFetcher(render_method=render_method, wait_time=wait_time, inline_resources=inline_resources)
    
    # 获取URL内容
    html_content, text_content, title, status_code = fetcher.fetch_url(url)
    
    if html_content is None:
        return None, title or url, status_code
    
    # 如果没有提供文件名，从URL生成一个
    if filename is None:
        # 从URL中提取域名
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # 生成文件名: 域名-时间戳.html
        timestamp = int(time.time())
        random_id = random.randint(1000, 9999)
        filename = f"{domain}-{timestamp}-{random_id}"
    
    # 确保输出目录存在
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存HTML内容
    html_filename = f"{filename}.html"
    html_path = output_dir / html_filename
    saved_html_path = fetcher.save_html_to_file(html_content, html_path)
    
    # 不再保存文本内容
    # text_filename = f"{filename}.txt"
    # text_path = output_dir / text_filename
    # saved_text_path = fetcher.save_text_to_file(text_content, text_path)
    
    return {
        "html_path": str(saved_html_path),
        # "text_path": str(saved_text_path),  # 移除文本路径
        "title": title,
        "url": url,
        "render_method": render_method
    }, title, status_code

def install_dependencies():
    """安装依赖库"""
    try:
        import subprocess
        
        # 安装基本依赖
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"], check=True)
        
        # 安装浏览器自动化依赖
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
            subprocess.run(["playwright", "install", "chromium"], check=True)
            print("Playwright安装成功！")
        except Exception as e:
            print(f"Playwright安装失败: {str(e)}")
            
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
            print("Selenium安装成功！")
        except Exception as e:
            print(f"Selenium安装失败: {str(e)}")
            
        print("所有依赖安装完成！")
        return True
    except Exception as e:
        print(f"安装依赖时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 简单测试
    url = "https://www.example.com"
    output_dir = "./test_output"
    
    # 安装依赖库（如有必要）
    if not has_playwright and not has_selenium:
        print("未检测到浏览器渲染库，尝试安装...")
        install_dependencies()
    
    # 测试不同渲染方法
    render_methods = [m for m in [RENDER_METHOD_PLAYWRIGHT if has_playwright else None,
                                 RENDER_METHOD_SELENIUM if has_selenium else None,
                                 RENDER_METHOD_REQUESTS] if m]
    
    for method in render_methods:
        print(f"\n测试 {method} 渲染方法:")
        result, title, status = fetch_and_save_url(url, output_dir, render_method=method)
        
        if result:
            print(f"标题: {title}")
            print(f"HTML文件: {result['html_path']}")
            # 不再输出文本文件路径，因为我们不再保存文本文件
        else:
            print(f"获取失败: {status}")