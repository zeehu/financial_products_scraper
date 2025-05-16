import json
import os
import math
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class ChinaWealthScraper(BaseScraper):
    """中国财富网理财产品爬虫"""
    
    BASE_URL = "https://www.chinawealth.com.cn/zzlc/jsp/lccp.jsp"
    API_URL = "https://www.chinawealth.com.cn/LcSolrSearch.go"
    
    def __init__(self, use_proxy: bool = False, **kwargs):
        """初始化中国财富网爬虫"""
        super().__init__(use_proxy=use_proxy, **kwargs)
        
        # 设置请求头
        self.headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.chinawealth.com.cn",
            "Referer": "https://www.chinawealth.com.cn/zzlc/jsp/lccp.jsp",
            "X-Requested-With": "XMLHttpRequest"
        }
            
    def _get_product_name(self, product_data: dict) -> str:
        """获取产品名称"""
        try:
            copy_list = product_data.get("copy", [])
            if isinstance(copy_list, list) and len(copy_list) > 2:
                return copy_list[2]
            return product_data.get("cpms", "")  # 尝试使用备选字段
        except Exception:
            return product_data.get("cpms", "")  # 出错时使用备选字段
            
    def _process_basic_info(self, product_data: dict) -> dict:
        """处理产品基本信息"""
        return {
            "product_id": product_data.get("id", ""),
            "product_code": product_data.get("cpdjbm", ""),
            "product_name": self._get_product_name(product_data),
            "issuer": product_data.get("fxjgms", ""),
            "issuer_code": product_data.get("fxjgdm", ""),
            "risk_level": product_data.get("fxdjms", ""),
            "risk_level_code": product_data.get("cpfxdj", ""),
            "product_type": product_data.get("cptzxzms", ""),
            "product_type_code": product_data.get("cptzxz", ""),
            "currency": product_data.get("mjbz", ""),
            "investment_period": product_data.get("qxms", ""),
            "min_investment": product_data.get("qdxsjef", ""),
            "sale_status": product_data.get("syztdm", ""),
            "sale_regions": product_data.get("cpxsqy", ""),
            "start_date": product_data.get("cpqsrq", ""),
            "end_date": product_data.get("cpyjzzrq", ""),  # 结束日期
            "product_category": product_data.get("cplx", ""),
            "income_type": product_data.get("cpsylx", ""),
            "sale_method": product_data.get("sfxcp", ""),
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    def _clean_nav_value(self, value: str) -> float:
        """清理并验证净值数据"""
        try:
            if not value or value == "--" or value == "null":
                return 0.0
            # 移除空格并转换为浮点数
            cleaned_value = value.strip()
            return float(cleaned_value)
        except (ValueError, TypeError):
            return 0.0
        
    def _process_nav_data(self, product_data: dict) -> Optional[dict]:
        """处理产品净值数据"""
        # 获取并清理净值数据
        initial_nav = self._clean_nav_value(product_data.get("csjz", ""))
        accumulated_nav = self._clean_nav_value(product_data.get("ljjz", ""))
        current_nav = self._clean_nav_value(product_data.get("cpjz", ""))
        
        # 检查是否有任何有效的净值数据（大于0）
        if not any([initial_nav > 0, accumulated_nav > 0, current_nav > 0]):
            return None
            
        return {
            "product_id": product_data.get("id", ""),
            "product_code": product_data.get("cpdjbm", ""),
            "initial_nav": initial_nav if initial_nav > 0 else None,  # 初始净值
            "accumulated_nav": accumulated_nav if accumulated_nav > 0 else None,  # 累积净值
            "current_nav": current_nav if current_nav > 0 else None,  # 产品净值
            "nav_date": datetime.now().strftime("%Y-%m-%d"),  # 净值日期
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _init_session(self) -> bool:
        """初始化会话，获取必要的Cookie"""
        try:
            # 访问主页获取初始Cookie
            response = self.session.get(
                self.BASE_URL,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # 等待Cookie设置
            self._wait()
            
            # 保存获取到的Cookie
            if 'Set-Cookie' in response.headers:
                logger.info("成功获取新的Cookie")
            
            return True
        except Exception as e:
            logger.error(f"初始化会话失败: {str(e)}")
            return False

    def _fetch_page(self, page: int) -> Tuple[List[dict], int]:
        """获取指定页码的数据"""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 构建请求参数
                params = {
                    "cpjglb": "",
                    "cpyzms": "01,03",  # 产品运作模式
                    "cptzxz": "",
                    "cpfxdj": "01,02",
                    "cpqx": "",
                    "mjbz": "",
                    "cpzt": "02,04",  # 产品状态
                    "mjfsdm": "01,NA",  # 募集方式代码
                    "cptssx": "",
                    "cpdjbm": "",
                    "cpmc": "",
                    "cpfxjg": "",
                    "yjbjjzStart": "",
                    "yjbjjzEnd": "",
                    "areacode": "",
                    "pagenum": str(page),  # 页码
                    "orderby": "",
                    "code": "",
                    "sySearch": -1,
                    "changeTableFlage": 0
                }
                
                # 请求等待
                self._wait(retry_count)
                
                # 更新请求头
                self.headers["User-Agent"] = self._get_random_user_agent()
                
                # 发起请求
                response = self.session.post(
                    self.API_URL,
                    headers=self.headers,
                    data=params,
                    proxies=self.proxies,
                    timeout=self.timeout
                )
                
                # 检查响应状态码
                response.raise_for_status()
                
                # 保存响应内容
                self._save_response(page, retry_count, response)
                
                # 检查是否返回错误码
                try:
                    data = response.json()
                    if data.get("code") == "error":
                        logger.warning(f"第 {page} 页返回错误码，可能触发了访问限制")
                        retry_count += 1
                        
                        # 如果遇到错误，重新初始化会话并等待更长时间
                        self._init_session()
                        self._wait(retry_count * 2)
                        continue
                    
                    products = data.get("List", [])
                    total_count = data.get("Count", 0)
                    
                    if products:
                        return products, total_count
                    else:
                        logger.warning(f"第 {page} 页返回空数据，尝试重试")
                        retry_count += 1
                        continue
                    
                except json.JSONDecodeError:
                    logger.error(f"JSON解析错误，响应内容：{response.text[:200]}...")
                    retry_count += 1
                    continue
                
            except Exception as e:
                logger.error(f"获取第 {page} 页数据时发生错误: {str(e)}")
                retry_count += 1
                self._wait(retry_count * 2)
                continue
        
        logger.error(f"获取第 {page} 页数据失败，已达到最大重试次数")
        return [], 0
    
    def _save_response(self, page: int, retry_count: int, response):
        """保存响应内容用于调试"""
        try:
            debug_dir = os.path.join(os.getcwd(), 'data', 'debug')
            os.makedirs(debug_dir, exist_ok=True)
            
            debug_file = os.path.join(
                debug_dir, 
                f"api_response_page{page}_try{retry_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(f"Status Code: {response.status_code}\n")
                f.write(f"Headers: {dict(response.headers)}\n")
                f.write(f"Response Text: {response.text}\n")
        except Exception as e:
            logger.warning(f"保存响应内容失败: {str(e)}")

    def scrape(self, max_pages: int = None) -> Tuple[List[Dict], List[Dict]]:
        """
        执行爬取任务
        
        Args:
            max_pages: 最大页数限制，为None表示不限制
            
        Returns:
            (产品基本信息列表, 产品净值信息列表)
        """
        # 产品信息和净值数据列表
        basic_info_list = []
        nav_data_list = []
        
        try:
            # 初始化会话
            if not self._init_session():
                logger.error("会话初始化失败，退出爬取")
                return basic_info_list, nav_data_list
            
            # 获取第一页数据以获取总数
            products, total_count = self._fetch_page(1)
            if not products:
                logger.warning("未获取到产品数据")
                return basic_info_list, nav_data_list
            
            logger.info(f"总共有 {total_count} 条产品数据")
            
            # 处理第一页数据
            for product in products:
                try:
                    basic_info = self._process_basic_info(product)
                    if basic_info:
                        basic_info_list.append(basic_info)
                        
                    nav_data = self._process_nav_data(product)
                    if nav_data:
                        nav_data_list.append(nav_data)
                except Exception as e:
                    logger.error(f"处理产品数据时出错: {str(e)}")
                    continue
            
            # 计算总页数
            page_size = 100  # 每页数据量
            total_pages = math.ceil(total_count / page_size)
            if max_pages:
                total_pages = min(total_pages, max_pages)
            
            # 获取剩余页面数据
            for page in range(2, total_pages + 1):
                logger.info(f"正在获取第 {page}/{total_pages} 页数据")
                
                products, _ = self._fetch_page(page)
                
                if products:
                    for product in products:
                        try:
                            basic_info = self._process_basic_info(product)
                            if basic_info:
                                basic_info_list.append(basic_info)
                                
                            nav_data = self._process_nav_data(product)
                            if nav_data:
                                nav_data_list.append(nav_data)
                        except Exception as e:
                            logger.error(f"处理产品数据时出错: {str(e)}")
                            continue
                else:
                    logger.error(f"第 {page} 页数据获取失败")
                    continue
            
            logger.info(f"成功处理 {len(basic_info_list)} 条产品数据")
            logger.info(f"成功处理 {len(nav_data_list)} 条净值数据")
            
        except Exception as e:
            logger.error(f"爬取过程中出错: {str(e)}")
        
        return basic_info_list, nav_data_list 
