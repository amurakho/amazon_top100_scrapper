#There scrappers for Amazon

amazon_get_categories. First scrapper to create a csv base of categories
get_links. Second scrapper which take a category from csv-category-base, getting the the product urls and store in in SQL
get_descr. Last scrapper which take a product-link from SQL get JUST PRODUCT DESCRIPTION(also append title) AND ASIN (IF YOU NEED MORE, I CAN USE ANOTHER SCRAPPER FROM GITHUB. UNFORTUNATELY IT HAVE A BAD CODE.) and store it in Mongo
NOTE: get_descr-scrapper use AmazonMongoManage-class which you can find in github

#TODO:

1. Clear the description from "bad" words(TF-IDF or some like this). And get the list of keywords

2. Create keyword-scrapper(or edit my old amazon-scrapper from github). And parse new products description

3. Clear new descriptions and connect it with old producs by category

4. Repeat 2-3.

5 .script which will realize connection ASIN-KEYWORD. Logic: 5.1 User give the ASIN. 5.2 Find product with this ASIN(category) 5.3 Return keywords with this category(maybe with product, but i should analize it)

6. OPTIONAL: Create simple Django/Flask(maybe aiohttp!!) service to monitor the connection: ASIN-KEYWORD/KEYWORD-ASIN

7. OPTIONAL: Need to analyze ASIN. Maybe i will connect keywords with ASIN without connection with category