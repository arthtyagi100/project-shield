# project-shield

Just completed my project, Project Shield — A Serverless PII Redaction Web Application!

Let me tell you what it is, I could have asked AI to draft me a post but whats the fun in that.

So, what it does it, it hides your personal information from documents you submit, say bye bye to manual redactions! You just upload your documents and boom, you can download the redacted ones. 

This works with AWS Comprehend, it basically --(is a managed natural language processing (NLP) service that uses machine learning to extract insights, meaning, and relationships from unstructured text.)-- Simplifying to it detects insights from texts. 

I have my Lambda setup, that is triggered every time you upload a document, which then talks to AWS Comprehend, hey could you redact personal information from this please!
And Comprehend says why not and returns the redacted document, which then is for you to download.

Well, this was a piece of cake, I wish. Writing code was one part of the story, setting up routes, maintaining security, troubleshooting was the other. But it was fun!

if you wanna know more internal tech so, document sends api call to my api gateway, which then talks to my lambda function, which then gets the presigned url from the s3 bucket, which is sent to the user to upload file, after file upload, s3 triggers lambda, which then connects to comprehend, which returns the string to be redacted. Lambda then have to reverse the order of the words to make the formatting correct. after which it redacts and sends the file to the ouput s3 bucket, whose presigned url is returned to the user. If that make sense 😅 

Right now, this only works for text type documents, I am still working to bring it to other types as well. 
Feel free to check it out and of course drop suggestions in comments - https://lnkd.in/gSJuJUKG
