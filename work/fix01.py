from helpers import *
fx={}
fx["FNCE 2025|Lakanto"]=dict(Email="""Hi {{first_name}},

Saw that Lakanto exhibited at FNCE last year.

From what we can see, Lakanto does roughly $1.4M a month on Amazon, sold direct, with over 200,000 reviews across the catalog. The trend over the last 12 months is close to flat though, and last month was down, which for a brand with that review base usually means the channel is being maintained rather than pushed.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations. We helped MouthWatchers grow from roughly $40K a month to $1M a month, and it wasn't just ad spend.

Would it make sense to have a quick conversation?

Yoni
""",QA_Flags_add="trimmed for length")
fx["FNCE 2025|Jones & Bartlett Learning"]=dict(Email="""Hi {{first_name}},

Saw that Jones & Bartlett Learning exhibited at FNCE last year.

From what we can see, Jones & Bartlett titles do somewhere around $900k a month on Amazon, and only about a fifth of that is sold by Amazon itself. The largest seller of your books there is a third-party reseller at roughly 30%, and we don't see a Jones & Bartlett seller account in the mix at all.

For a publisher that means the new copy Buy Box, pricing and listing content on your top titles are largely in other hands.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Open to a short call on it?

Yoni
""",QA_Flags_add="trimmed for length")
fx["FNCE 2025|Fishwife Tinned Seafood Co."]=dict(Email="""Hi {{first_name}},

Saw that Fishwife exhibited at FNCE last year.

From what we can see, Fishwife is doing roughly $780k a month on Amazon and has grown a lot over the last year. About 55% is through your own account, with the rest split between Amazon as the vendor and Whole Foods Market's Amazon storefront. Amazon's share jumped last month while your direct share dropped, and once 1P takes the Buy Box on the sardine and salmon packs, the pricing moves with it.

We manage Amazon for brands end to end, including hybrid 1P/3P setups decided at the product level.

Open to a short call on keeping control of that mix?

Yoni
""",QA_Flags_add="trimmed for length")
fx["Las Vegas Souvenir & Resort Gift Show 2026|MasterPieces Inc."]=dict(Email="""Hi {{first_name}},

Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week.

From what we can see, MasterPieces does roughly $760k a month on Amazon, sold direct, across about 2,600 listings with a 4.6 average rating. The top seller is puzzle glue at around $40k a month, and after the first few puzzles the revenue per listing drops off fast. That is a long tail of licensed puzzles and games that mostly isn't being advertised or merchandised.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Is it worth a short call on getting more out of the catalog?

Yoni
""",QA_Flags_add="trimmed for length")
update_rows(fx)
# re-run QA on all rows with the fixed checker to clear the false flags
df=pd.read_csv(CKPT,dtype=str,keep_default_na=False)
for i,r in df.iterrows():
    flags,wc=qa_email(r['Subject'],r['Email'])
    qa=[x for x in r['QA_Flags'].split('; ') if x and not x.startswith('QA_AUTO:')]
    if flags: qa.append('QA_AUTO:'+','.join(flags)); print('FLAG',r['exhibitor'],flags,wc)
    df.at[i,'QA_Flags']='; '.join(qa)
df.to_csv(CKPT,index=False)
print(status())
