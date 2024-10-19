from .__version__ import __version__
import subprocess
import json
import os
from urllib.parse import urlparse
from b_hunters.bhunter import BHunters
from karton.core import Task
import re
def split_url(url):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    path = parsed_url.path.lstrip('/')  # Remove leading slashes
    query = parsed_url.query

    if not path:
        path = ""  # Set path to None if it's empty
    if query:
        path += '?' + query  # Append query parameters to the path

    if scheme and netloc:
        if scheme.endswith('://'):
            scheme = scheme[:-3]  # Remove the trailing '://'
        if netloc.endswith('/'):
            netloc = netloc[:-1]  # Remove trailing slash from netloc
        return scheme + '://' + netloc, path
    else:
        return netloc, path


class dirsearchm(BHunters):
    """
    B-Hunters dirsearch developed by Bormaa
    """

    identity = "B-Hunters-dirsearch"
    version = __version__
    persistent = True
    filters = [
        {
            "type": "subdomain", "stage": "new"
        }
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    def dirsearchcommand(self,url):
        result=[]
        result403=[]
        newurls=[]
        outputfile=self.generate_random_filename()

        try:
            try:
                output = subprocess.run(["dirsearch","-x","404,429,503,502,406,520,400,409,500","-u",url,"--random-agent","--crawl","-o",outputfile,"--format","json","-r","--max-recursion-depth","4","--recursion-status","200-403","--crawl","-t","150"],capture_output=True,text=True,timeout=1200)  # 20 minutes timeout
            except subprocess.TimeoutExpired:
                self.log.warning(f"Dirsearch process timed out for URL: {url}")
            if os.path.exists(outputfile):
                with open(outputfile, "r") as file:
                    data = json.load(file)
                for i in data["results"]:
                    status=i['status']
                    length=i['content-length']
                    pathurl=i['url']
                    fuzz=f"{status} - {length} {pathurl}"    
                    if pathurl[-1]=="/":
                        newurls.append(pathurl)
                    if status==403 or status==401 :
                        result403.append({"status":status,"pathurl":pathurl,"lengrh":length})
                    else:
                        if not ((status == 302 and "/etc/passwd" in pathurl) or ("favicon.ico" in pathurl) or (status != 302 and "google.com" in pathurl)) :
                            if status !=301:
                                result.append(fuzz)
                os.remove(outputfile)

        except Exception as e:
            self.log.error("Error happened with direseach")
            self.log.error(e)

            raise Exception(e)

        return result,result403,newurls
                
    def scan(self,url):        
        result,result403,newurls=self.dirsearchcommand(url)
        return result,result403,newurls
        
    def process(self, task: Task) -> None:
        url = task.payload["data"]
        self.log.info("Starting processing new url")
        domain = re.sub(r'^https?://', '', url)
        domain = domain.rstrip('/')
        self.log.info(domain)

        self.update_task_status(domain,"Started")
        try:
            result,result403,newurls=self.scan(url)
            collection=self.db["domains"]
            if result !=[]:
                self.send_discord_webhook(f"{self.identity} Results for {domain}","\n".join(result),"main")
                if self.db.client.is_primary:
                    update_result = collection.update_one({"Domain": domain}, {'$push': {'Paths': result, 'Paths403': result403}})
                    if update_result.modified_count == 0:
                        self.log.warning(f"Update failed for domain {domain}. Document not found or no changes made.")
                        # Optionally, you can check if the document exists
                        if collection.count_documents({"Domain": domain}) == 0:
                            self.log.error(f"Document for domain {domain} does not exist in the collection.")
                        else:
                            self.log.info(f"Document exists for {domain}, but no changes were made. Possibly duplicate data.")
                    else:
                        self.log.info(f"Successfully updated document for domain {domain}")
                else:
                    raise Exception("MongoDB connection is not active. Update operation aborted.")

            for i in newurls:
                newurl_task = Task(
                        {"type": "path", "stage": "new"},
                        payload={"data": i,
                        "source":"dirsearch"
                        }
                    )
                self.send_task(newurl_task)
                
            # for i in result403:
            #     try:
            #         pathurl=i["pathurl"]
            #         domain,path=split_url(pathurl)
            #         if "." not in  path:
                        
            #             tag_task = Task(
            #                 {"type": "url", "stage": "403"},
            #                 payload={"data": i,
            #                 "module":"dirsearch"
            #                 }
            #             )
            #             self.send_task(tag_task)
            #     except Exception as e:
            #         self.log.error(e)
            self.update_task_status(domain,"Finished")
        except Exception as e:
            self.update_task_status(domain,"Failed")
            raise Exception(e)
            self.log.error(e)
