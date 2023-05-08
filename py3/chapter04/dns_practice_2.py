import dns.resolver


name = 'python3.info'

answer = dns.resolver.resolve(name, 'MX')
print(answer.rrset)