from dotenv import load_dotenv

from dana.contrib.knows import Kpk


load_dotenv()


kpk = Kpk("s3://aitomatic-public/dxkb/finance/financebench")

kpk.organize(force=True)
