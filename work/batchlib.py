from helpers import *
def P(brand,cat,sub,sellers,single,store,url,amz,mom,mom12,price,rating,prods,revs,monthly,ttm):
    return {"Brand Name":brand,"Primary Category":cat,"Primary Subcategory":sub,"Average Sellers":sellers,"Single Seller Name":single,"Has Storefront":str(store).lower(),"Storefront URL":url,"Average Amazon Revenue %":amz,"Average MoM Growth":mom,"Average 12-Month MoM Growth":mom12,"Average Price":price,"Average Rating":rating,"Total Products":prods,"Total Reviews":revs,"Total Monthly Revenue":monthly,"Trailing 12-Month Revenue":ttm}
def S(*pairs): return [{"Seller Name":n,"Estimated Brand Share":s} for n,s in pairs]
def T(*trip): return [{"Product Title":t,"ASIN":a,"Monthly Revenue Estimate":r} for t,a,r in trip]
def RAW(profile,sellers,products): return {"profile":[profile] if profile else [],"sellers":sellers,"products":products}
def E(row,key,brand_query,angle,points,subject,email,conf=None,brand_sellers=None,qa=None):
    return dict(row=row,key=key,brand_query=brand_query,angle=angle,angle_points=points,subject=subject,email=email.strip()+"\n",conf=conf,brand_sellers=brand_sellers,qa_flags=qa or [])
def run(raw,emails):
    n=append_rows(emails,raw); d,t,nf=status(); print(f"appended {n}; {d}/{t} rows total, {nf} SmartScout not found")
