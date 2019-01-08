# One express article

# from utils import RegexSplitterEnv
# env = RegexSplitterEnv(r'class=\"content\"\ content-iframe>(.*<footer>)',
# post_processors=["remove_tags", "remove_trailing_spaces"])
# env.load_page("https://expres.online/news/filaretovi-prisvoeno-zvannya-geroya-ukraini")
# # env.test()
# env.test_gui() # - helps to create perfect regex pattern!

# Get links

# from utils import RegexSplitterEnv
# env = RegexSplitterEnv(r'(https:\/\/expres\.online\/news\/[a-zA-z0-9-]+)\"')
# env.load_page("https://expres.online/news?page=2")
# env.test()
# # env.test_gui() # - helps to create perfect regex pattern!


from utils import RegexSplitterEnv
env = RegexSplitterEnv(r'class=\"content\"\ content-iframe>(.*<footer>)', )
env.load_page("https://www.moex.com/ru/derivatives/money/currency/")
# env.test()
env.test_gui(1) # - helps to create perfect regex pattern!