"""
Configuration: Change this
"""
"""Your Steem account name:"""
authortowatch = "steemusername"
"""Your Whaleshares account name:"""
wlsaccount = "wlsusername"
"""Your Whaleshares private posting key:"""
wlspostingkey = "YOURPRIVATEPOSTINGKEYFORWHALESHARES"
"""Tags to use on whaleshares:"""
wlstags = '{"tags":["photography","photo","photofeed","travel","steemit"]}'

"""
Script: Don't change anything here unless you know what you are doing
"""
from beem import Steem
from beem.nodelist import NodeList
from beem.blockchain import Blockchain
from beem.comment import Comment
from beem.utils import construct_authorperm
from datetime import timedelta
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
stmnodes = NodeList().get_nodes()
stm = Steem(nodes=stmnodes)
wlsnode = 'https://rpc.wls.services/'
wls = Steem(node=wlsnode, keys=[wlspostingkey])
blockchain = Blockchain(steem_instance=stm)

def steem_to_wls():
    stream = map(Comment, blockchain.stream(opNames=['comment']))
    processed_posts = []
    while True:
        for post in stream:
            try:
                post.refresh()
                if post.is_main_post() and post['author'] == authortowatch:
                    authorperm = construct_authorperm(post['author'], post['permlink'])
                    if post.time_elapsed() > timedelta(minutes=2) or authorperm in processed_posts:
                        """Ignore updated posts"""
                        continue
                    try:
                        """Post to Whaleshares"""
                        title = post['title']
                        body = post['body']
                        tags = wlstags
                        wls.post(title, body, author=wlsaccount, json_metadata=tags, steem_instance=wls)
                        processed_posts += [authorperm]
                        logger.info("Posted post to Whaleshares: "+title)
                    except Exception as error:
                        logger.warning("Could not post to Whaleshares: "+repr(error))
            except:
                continue
if __name__ == '__main__':
    logger.info("Started")
    steem_to_wls()