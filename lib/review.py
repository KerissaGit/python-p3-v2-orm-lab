from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @property
    def year(self):
        return self._year
    
    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an interger")
        if value < 2000:
            raise ValueError("Year must be 2000 or later")
        self._year = value

    @property
    def summary(self):
        return self._summary
    
    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("Summary must be a string")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id
    
    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Employee ID must be an integer")
        CURSOR.execute("SELECT id FROM employees WHERE id = ?;", (value,))
        if not CURSOR.fetchone():
            raise ValueError(f"Employee ID {value} does not exist")
        self._employee_id = value


    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        try:
            CURSOR.execute("""
                INSERT  INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?);
            """, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        except Exception as e:
            return e

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        if not isinstance(employee_id, int):
            raise ValueError("Employee ID must be an integer")
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        if row is None:
            return None
        review_id, year, summary, employee_id = row
        return cls(year, summary, employee_id, id=review_id)
   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        try:
            CURSOR.execute("SELECT * FROM reviews WHERE id = ?;", (id,))
            row = CURSOR.fetchone()
            return cls.instance_from_db(row)
        except Exception as e:
            return e

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        try:
            if not isinstance(self.employee_id, int):
                raise ValueError("Employee ID must be an integer")
            CURSOR.execute("""
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?;
            """, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()
        except Exception as e:
            return e

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        try:
            CURSOR.execute("DELETE FROM reviews WHERE id = ?;", (self.id,))
            CONN.commit()
            del Review.all[self.id]
            self.id = None
        except Exception as e:
            return e

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        try:
            CURSOR.execute("SELECT * FROM reviews;")
            rows = CURSOR.fetchall()
            return [cls.instance_from_db(row) for row in rows]
        except Exception as e:
            return e

