import atexit
import sqlite3
import sqlparse
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
    QDialog
)


class DatabaseTool(QMainWindow):
    """
    A GUI tool for executing SQL queries on a SQLite database.
    """

    def __init__(self):
        """
        Initializes the GUI and sets up the UI elements.
        """
        super().__init__()

        # Set window properties
        self.setWindowTitle("Database Tool")
        self.resize(400, 300)

        # Initialize connection variable
        self.conn = None

        # Create UI elements
        self.table = QTableWidget()
        self.query_box = QTextEdit()
        self.execute_btn = QPushButton("Execute Query")
        self.prettify_btn = QPushButton("Prettify SQL")
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")

        # Set initial table properties
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        mid_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # Add UI elements to layouts
        top_layout.addWidget(self.query_box)
        mid_layout.addWidget(self.prettify_btn)
        mid_layout.addWidget(self.execute_btn)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(mid_layout)
        main_layout.addWidget(self.table)
        bottom_layout.addWidget(self.connect_btn)
        bottom_layout.addWidget(self.disconnect_btn)
        main_layout.addLayout(bottom_layout)
        main_widget.setLayout(main_layout)

        # Connect UI element actions to buttons
        self.execute_btn.clicked.connect(self.execute_query)
        self.prettify_btn.clicked.connect(self.prettify_query)
        self.connect_btn.clicked.connect(self.connect_database)
        self.disconnect_btn.clicked.connect(self.disconnect_database)

        # Register a disconnect handler to ensure the database connection is closed on exit
        atexit.register(self.disconnect_database)

    def prettify_query(self):
        """
        Prettifies the SQL query entered in the query box.
        """
        try:
            self.query_box.setText(
                sqlparse.format(
                    self.query_box.toPlainText(),
                    reindent=True,
                    keyword_case='upper'))
        except Exception as err:
            QMessageBox.warning(self, "Error", str(err))

    def connect_database(self):
        """
        Opens a connection to the database using the connection string entered in the query box.
        """
        try:
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("Database Files (*.db *.sqlite)")
            if file_dialog.exec_() == QDialog.Accepted:
                database_filename = file_dialog.selectedFiles()[0]
                self.conn = sqlite3.connect(
                    database_filename,
                    check_same_thread=False)
                QMessageBox.information(
                    self, "Connection Status", "Connected to database file " + database_filename)
        except Exception as err:
            QMessageBox.warning(self, "Error", str(err))

    def disconnect_database(self):
        """
        Closes the connection to the database.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            QMessageBox.information(
                self, "Connection Status", "Disconnected from database")

    def execute_query(self):
        """
        Executes the SQL query entered in the query box and displays the results if any in the table.
        """
        if not self.conn:
            QMessageBox.warning(self, "Error", "Not connected to a database")
            return
        try:
            query = self.query_box.toPlainText()
            cursor = self.conn.cursor()
            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                rows = cursor.fetchall()

                columns = [description[0]
                           for description in cursor.description]
                if rows:
                    self.table.setRowCount(len(rows))
                    self.table.setColumnCount(len(columns))
                    self.table.setHorizontalHeaderLabels(columns)
                    for i, row in enumerate(rows):
                        for j, col in enumerate(row):
                            item = QTableWidgetItem(str(col))
                            self.table.setItem(i, j, item)
                    self.table.resizeColumnsToContents()
                else:
                    QMessageBox.information(
                        self, "Information", "Query returned no rows.")
            else:
                self.conn.commit()
                QMessageBox.information(
                    self, "Information", "Transaction committed successfully.")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as err:
            QMessageBox.warning(self, "Error", str(err))
        finally:
            cursor.close()


if __name__ == "__main__":
    app = QApplication([])
    window = DatabaseTool()
    window.show()
    app.exec_()
