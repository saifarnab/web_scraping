from facebook_scraper import get_posts, set_cookies


def run():
    # for post in get_posts('wynnlasvegas', pages=4):
    #     post_id = "pfbid02VtXsH2T7xBMcbUtJkixy89kAo5MrhpPLAQxubXXgfB9N3Lgq1NfCUrZPVAXWwTiTl"
    #     gen = get_posts(
    #         post_urls=[post_id],
    #         options={
    #             "comments": True,
    #             "allow_extra_requests": True,
    #             "comment_reactors": True,
    #             "reactions": True,
    #             "extra_info": True,
    #         },
    #     )
    #     post_item = next(gen)
    #     comments = post_item['comments_full']
    #     for comment in comments:
    #
    #         # e.g. ...print them
    #         print(comment)
    #
    #         # e.g. ...get the replies for them
    #         for reply in comment['replies']:
    #             print(' ', reply)
    #             break
    #         break

    # set_cookies("cookies.json")
    post = next(get_posts(post_urls=['1210214419806423'], options={"comments": True}))
    print(
        f"Comments: {post['comments']}, Top level comments: {len(post['comments_full'])}, Replies: {sum(len(c['replies']) for c in post['comments_full'])}")



run()
