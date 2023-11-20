import PyPDF2
import os
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

START_TIME = default_timer()

def check_pdf(name):
    try:
        PyPDF2.PdfFileReader(open(os.path.join(os.path.abspath('.'),'pdf',name), "rb"))
        return 1
    except PyPDF2.utils.PdfReadError:
        print("invalid PDF file : pypdf2 check")
        return 0
    else:
        return 0



def fetch(session, csv):
    name = csv.split('/')[-1].split('.')[0]
    print(name)
    with session.get(csv,stream=True,allow_redirects=True) as r:
        if r.status_code != 404:
            with open(os.path.join(os.path.abspath('.'),'pdf',name+'.pdf'),'wb') as f:
                f.write(r.content)
            f.close()
            flag = check_pdf(name+'.pdf')

            if flag == 1:
                return (1,csv)
            else:
                return (0,csv)
        else:
            return (0,csv)

async def get_data_asynchronous(csvs_to_fetch):
    
    print("{0:<30} {1:>20}".format("File", "Completed at"))
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, csv) # Allows us to pass in multiple arguments to `fetch`
                )
                for csv in csvs_to_fetch
            ]
            k=[]
            for response in await asyncio.gather(*tasks):
                
                k.append(response)
    return k

def main(pdf_links):
    
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    
    future = asyncio.ensure_future(get_data_asynchronous(pdf_links))
    loop.run_until_complete(future)

    return future.result()

def save_pdf(pdf_links):

    pdf_res = main(pdf_links)
    
    pdf_paths = [x[1] for x in pdf_res if x[0]==1]
    
    return pdf_paths

if __name__ == '__main__':

    pdf_links=["https://cdn.s3waas.gov.in/s338b3eff8baf56627478ec76a704e9b52/uploads/2020/06/2020060216.pdf",
    "https://cdn.s3waas.gov.in/s338b3eff8baf56627478ec76a704e9b52/uploads/2020/06/2020060216.pdf"]
    pdf_paths = save_pdf(pdf_links)

    print(pdf_paths)


