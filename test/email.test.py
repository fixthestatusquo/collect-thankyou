from thankyou import Email

eml = Email("https://collect-backend.campax.org/wp-json/wp/v2/campaign/51", sender=Email.address('Test', 'dump+test1@cahoots.pl'))

eml.fetch()

eml.add_attachment('article-for-you.pdf', open('test/test.pdf', 'rb').read())

contact = {
    'firstName': 'Marcin',
    'email': 'dump@cahoots.pl'
}
msg = eml.build(contact)


eml.send(msg)
