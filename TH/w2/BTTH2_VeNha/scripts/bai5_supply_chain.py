"""Bai 5: Mo phong chuoi cung ung + query event ProductUpdated."""
from ape import accounts, project, chain


def main():
    manager = accounts[0]
    farmer = accounts[1]
    warehouse = accounts[2]
    supermarket = accounts[3]

    sc = project.SupplyChain.deploy(sender=manager)
    print("SupplyChain at", sc.address)

    sc.addProduct(1, "Rau cai sach", sender=manager)
    print("1) addProduct:", sc.getProduct(1))

    # Nong dan -> kho lanh -> sieu thi
    sc.transferProduct(1, farmer, "tai_nong_dan", sender=manager)
    print("2) nong dan:", sc.getProduct(1))

    sc.transferProduct(1, warehouse, "kho_lanh", sender=manager)
    print("3) kho lanh:", sc.getProduct(1))

    sc.transferProduct(1, supermarket, "sieu_thi", sender=manager)
    print("4) sieu thi:", sc.getProduct(1))

    # Query logs ProductUpdated (Ape / web3 style)
    print("\n=== Event ProductUpdated (lich su) ===")
    logs = sc.ProductUpdated.query("*", start_block=0)
    for log in logs:
        print(log)


if __name__ == "__main__":
    main()
