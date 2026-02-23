from PyQt5.QtWidgets import QApplication
import sys
from SW_Tunning.core.workflow import MainWindow
from SW_Tunning.core.visa_setup import connect_instruments

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Connexion instruments (avec retry)
    scope, srfd_com, srfd_amp_master, srfd_amp_slave, swg33522B, swg33611A, com_status = connect_instruments()

    # Affichage statut communication
    if com_status is True:
        print("Communication OK du premier coup")
    elif com_status is False:
        print("⚠️ Première tentative échouée → Reconnexion réussie")
    else:
        print("❌ Communication impossible avec les instruments")

    # Lancement workflow
    w = MainWindow(scope, srfd_com, srfd_amp_master, srfd_amp_slave, swg33522B, swg33611A)
    w.show()

    sys.exit(app.exec_())
