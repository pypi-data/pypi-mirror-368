import json

if __name__ == '__main__':
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    request_verification_token = 'CfDJ8M6CuWz5hhxGnmUVXw2yDHQlfeNDzVoF03IbAJ0p3LdaDW7poklPvy74ykYda-qwcrtUXD4rnNzn583Ug7PWbR9IlomGzQh1OQIw_pa9d5TNwdN5p77SDfIfz3yq1nWPzxemEn_8bbh7TGGK9FIwcRY' 
    cookie = "_ga=GA1.1.478241025.1718907711; _ga_0623JYSC1Q=GS1.1.1718922743.2.0.1718922743.0.0.0; _ga_VW1SFWJKBB=GS1.1.1730789269.3.0.1730789272.0.0.0; _ga_CSLL4ZEK4L=GS1.1.1730789269.3.0.1730789272.0.0.0; _ga_NQ5ZN114SB=GS1.1.1730789269.3.0.1730789272.0.0.0; .AspNetCore.Session=CfDJ8M6CuWz5hhxGnmUVXw2yDHRQxNlIdqc8pBGKOJhMcHphMelhCyOQD7cnzYLVUWcsfCE8KOO8TNogarX5FbmvNQeSW1pTphWgR%2B6RLzPiUWuR4yPiDmb6rg82isfHqoEBhFoziXpFlU2o9pMgQICLsy7WbaeZbSgOl6FTg5Y0vLQ5; __RequestVerificationToken=CfDJ8M6CuWz5hhxGnmUVXw2yDHQXNjHWpjZ61I-CMSrl0yWsdWpCyt2QhUoeZ2L2aY0sqNpGy-wrD8ToMph6-wbfcRPpqORdlVci0ghxWu-3i4PCuWsiOkq90E1WupEYErSXnhsQVwHHGcD63WI7qyXZd7w; _ga_GNYE9X3V7H=GS1.1.1730825963.2.1.1730825988.0.0.0"

    headers = {
        'authority':       'infobridge.fhwa.dot.gov',
        'origin':          'https://infobridge.fhwa.dot.gov',
        'sec-fetch-site':  'same-origin',
        'sec-fetch-mode':  'cors',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',

        '__requestverificationtoken': request_verification_token,
        'user-agent': user_agent,
        'cookie': cookie
    }

    if len(sys.argv) == 1:
            
        headers.update({
            'x-requested-with': 'XMLHttpRequest',
            'content-type':     'application/json; charset=UTF-8',
            'accept':           'application/json, text/javascript, */*; q=0.01',
            'referer':          'https://infobridge.fhwa.dot.gov/Data',
        })

        bridgeTable = getBridgeList(headers, start_page=511, totalpages=808, pagesize=100)
        print(json.dumps(bridgeTable, indent=2))
        sys.exit()

    elif sys.argv[1] == "-S":
        headers.update({
            'datatype':     'json',
            'content-type': 'application/json; charset=UTF-8',
            'accept':       'application/json, text/plain, */*'
        })
        bridgeTable = json.load(open(sys.argv[1]))

        # calids = list(map(str.strip, open("init/calid.txt").readlines()))
        # bridgeTable = [i for i in bridgeTable if i["STRUCTURE_NUMBER"] in calids]


        # print(json.dumps(nbi_data, indent=2))

    else:
        headers.update({
            'datatype':     'json',
            'content-type': 'application/json; charset=UTF-8',
            'accept':       'application/json, text/plain, */*'
        })
        bridgeTable = json.load(open(sys.argv[1]))

        bridgeTable = [
            i for i in bridgeTable 
            if " " in i["STRUCTURE_NUMBER"] and len(i["STRUCTURE_NUMBER"]) in {7, 8}
        ]

        # calids = list(map(str.strip, open("init/calid.txt").readlines()))
        # bridgeTable = [i for i in bridgeTable if i["STRUCTURE_NUMBER"] in calids]
        if len(sys.argv) > 3:
            bridgeTable = [
                i for i in bridgeTable 
                if i["STRUCTURE_NUMBER"] == sys.argv[3]
            ]
            if len(bridgeTable) == 0:
                print(f"Structure {sys.argv[3]} not found", file=sys.stderr)
                sys.exit(1)
        else:
            bridgeTable = [
                i for i in bridgeTable 
                if " " in i["STRUCTURE_NUMBER"] and len(i["STRUCTURE_NUMBER"]) in {7, 8}
            ]

        nbi_data = getNBIData(headers, bridgeTable[:], years=(2024,)) #range(2020, 2024))
        print(json.dumps(nbi_data, indent=2))

