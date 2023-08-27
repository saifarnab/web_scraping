class Template:
    def __init__(self, contacts_first_name: str):
        self.contacts_first_name = contacts_first_name

    def get_email_template(self) -> str:
        return f"""<p dir=\"ltr\" id=\"isPasted\">Hi {self.contacts_first_name},</p><div color=\"rgb(75, 81, 93)\"><br>I'm curious if you've 
                    considered outsourcing your customer support?&nbsp;<br><br>I know that can be a scary thought–but we do things 
                    differently than you might have heard about or experienced.</div><div color=\"rgb(75, 81, 93)\"><br></div><div 
                    color=\"rgb(75, 81, 93)\">My name is Jim, and I'm the Co-Founder of xFusion. We offer a fully-managed customer 
                    support solution with a unique approach that combines human expertise and AI technology.</div>We're convinced 
                    that the foundation of outstanding customer support lies in having a valued and inspired team. We prioritize 
                    investing in our agents by providing attractive compensation and creating an enjoyable, supportive work 
                    atmosphere, which in turn generates top-notch service for our clients and their customers.<br><br>Because we 
                    empower our agents with the latest AI tools like ChatGPT and Intercom Fin, they\\'re up to 3x more productive 
                    than traditional customer support reps. This combination of technology and talent sets us 
                    apart.&nbsp;<br><br>Lastly, we understand the importance of trust when it comes to outsourcing, and we believe 
                    it\\'s our responsibility to earn your business. Therefore, no upfront payment is required. If you’re not happy 
                    after 30 days, you can walk and not pay a dime.<br><br>If you think having a short conversation makes sense, 
                    please let me know.<br><br>Thank you for taking the time to read this, {self.contacts_first_name}!<br><div color=\"rgb(75, 81, 
                    93)\">&nbsp;</div><div color=\"rgb(75, 81, 93)\">Jim - Co-Founder of <a fr-original-style=\"user-select: auto;\" 
                    href=\"http://xfusion.io/\" rel=\"noopener noreferrer noopener\" style=\"user-select: 
                    auto;\">xFusion.io</a></div><div color=\"rgb(75, 81, 93)\" data-en-clipboard=\"true\" data-pm-slice=\"1 1 []\">(
                    If you want me gone like a bad haircut, let me know and I\'ll disappear faster than a toupee in a 
                    hurricane)</div>"""
