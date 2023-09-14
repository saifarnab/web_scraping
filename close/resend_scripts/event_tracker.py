from typing import Union

import db_connectivity


class Event:

    def __init__(self, event_type: str, email_id: str):
        super().__init__()
        self.event_type = event_type
        self.email_id = email_id
        self.conn = None
        self.cursor = None

    def _set(self):
        self.conn, self.cursor = db_connectivity.db_connection()

    def get_sql(self) -> Union[str, None]:
        if self.event_type == 'email.sent':
            return f"UPDATE emails SET email_opened='Yes' WHERE resend_id='{self.email_id}'"
        elif self.event_type == 'email.delivered':
            return f"UPDATE emails SET email_delivered='Yes' WHERE resend_id='{self.email_id}'"
        elif self.event_type == 'email.complained':
            return f"UPDATE emails SET email_complained='Yes' WHERE resend_id='{self.email_id}'"
        elif self.event_type == 'email.delivered':
            return f"UPDATE emails SET email_delivered='Yes' WHERE resend_id='{self.email_id}'"
        elif self.event_type == 'email.bounced':
            return f"UPDATE emails SET email_bounced='Yes' WHERE resend_id='{self.email_id}'"
        elif self.event_type == 'email.opend':
            return f"UPDATE emails SET email_opend='Yes' WHERE resend_id='{self.email_id}'"
        elif self.event_type == 'email.clicked':
            return f"UPDATE emails SET email_clicked='Yes' WHERE resend_id='{self.email_id}'"
        return None

    def update_email(self):
        self._set()
        sql = self.get_sql()
        if sql is None:
            return
        self.cursor.execute(sql)
        self.conn.commit()
