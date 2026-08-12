import curl_cffi
import src.database
import src.parser
import time
import random
import src.shared
import src.telegram
from src.logger import logger, enable_file_logging, cleanup_old_logs

if __name__ == "__main__":
    cleanup_old_logs(7)
    enable_file_logging()

    while True:
        try:
            links = src.database.linkdb.get_links()
            new_links = set()
            for link in links:
                logger.info(f"scanning {link} link")
                try:
                    response = curl_cffi.get(link, timeout=(30, 60), impersonate="chrome")
                except Exception as e:
                    logger.warning(f"Failed to fetch {link}: {e}")
                    time.sleep(random.uniform(1, 3))
                    continue

                if response.status_code != 200:
                    print(f"Something went wrong with {link} status code: {response.status_code}")

                if not response.content:
                    logger.warning(f"Empty response from {link}, skipping")
                    continue

                content_type = src.parser.detect_type(response.headers.get("content-type"), link, response.content)
                if content_type == "HTML":
                    page_links = src.parser.extract_links(response.text, base_url=src.shared.BASE_URL)
                    page_links = [l for l in page_links if src.parser.is_allowed_domain(l, src.shared.BASE_URL)]
                    for new_link in page_links:
                        new_link = src.parser.normalize_url(new_link)
                        if not src.database.linkdb.exists(new_link) and src.parser.normalize_url(link) != new_link:
                            logger.info(f"[Loop-check-updates] on page {link} found a new {new_link} link")
                            src.telegram.send_message(f"• {new_link} found in {link}")
                            time.sleep(random.uniform(0.5, 1.5))
                            src.database.linkdb.insert(new_link)
                            new_links.add(new_link)

                    normalized_html = src.parser.normalize_html(response.text)

                    if not src.database.contentdb.exists(link):
                        logger.info(f"[Loop-check-updates] {link} does not exist in content database. Possibly a new/initial link")
                        src.database.contentdb.insert(link, content=normalized_html, content_type=content_type)
                        logger.info(f"[Loop-check-updates] Inserted {link} into content database")
                    else:
                        is_updated = src.database.contentdb.insert(link, content=normalized_html, content_type=content_type)
                        if is_updated:
                            logger.info(f"[Loop-check-updates] {link} have been updated")
                            src.telegram.send_message(f"• Site {link} updated")
                            time.sleep(random.uniform(0.5, 1.5))
                        else:
                            logger.debug(f"[Loop-check-updates] {link} is up-to-date")
                else:
                    if not src.database.contentdb.exists(link):
                        logger.info(f"[Loop-check-updates-file] {link} does not exist in content database. Possibly a new/initial file link")
                        src.database.contentdb.insert(link, data=response.content, content_type=content_type)
                        logger.info(f"[Loop-check-updates-file] Inserted {link} into content data database")
                    else:
                        is_updated = src.database.contentdb.insert(link, data=response.content, content_type=content_type)
                        if is_updated:
                            logger.info(f"[Loop-check-updates] {link} have been updated")
                            src.telegram.send_message(f"• File {link} updated")
                            time.sleep(random.uniform(0.5, 1.5))
                        else:
                            logger.debug(f"[Loop-check-updates] {link} is up-to-date")

                time.sleep(random.uniform(0.5, 1))

            # Checking new links
            if len(new_links) > 0:
                logger.info(f"found new {new_links} links")
                time.sleep(random.uniform(10, 30))
            else:
                logger.info("no new links found")
                time.sleep(random.uniform(3600, 7200))
        except KeyboardInterrupt:
            logger.info("stopped by user (KeyboardInterrupt)")
            break
        except SystemExit:
            logger.info("stopped by SystemExit")
            break
        except Exception as e:
            logger.exception(f"unexpected error in main loop: {e}")
            time.sleep(random.uniform(60, 300))