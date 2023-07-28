from odoo import fields, models, api,_
import psycopg2
from odoo.exceptions import ValidationError
from . import database


class UserWallet(models.Model):
    _name = 'user.wallet'
    _description = 'User Wallet'

    name = fields.Char('Wallet Address')
    private_key = fields.Char('Private Key')
    wallet_password = fields.Char('Wallet Password')
    wallet_balance = fields.Integer('Wallet Balance')
    uncleared_balance = fields.Integer('Uncleared Balance')
    db_id = fields.Integer('DataBase ID')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists !"),
    ]
    
    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()     
        res = super(UserWallet,self).create(vals)
        cur.execute("""insert into user_wallet
                (user_id,wallet_address,private_key,wallet_password,wallet_balance,uncleared_balance,wallet_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (res.create_uid.id,res.name,res.private_key,res.wallet_password,res.wallet_balance,res.uncleared_balance,res.id))
        cur.execute('''select id from user_wallet where wallet_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        conn.commit()
        cur.close()   
        return res
        
    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'request_details' in vals.keys():
            rec = [vals['request_details'],self.id]
            query = """Update user_wallet set transaction_id = %s where wallet_id = %s"""
            cur.execute(query,rec)
        conn.commit()
        cur.close()
        res = super(UserWallet,self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM user_wallet WHERE wallet_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(UserWallet, self).unlink()
        return res

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select wallet_id,wallet_address from user_wallet''')
            all_data= cur.fetchall()
            db_id=[]
            db_name=[]
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.name not in db_name:
                    cur.execute("""insert into user_wallet
                    (user_id,wallet_address,private_key,wallet_password,wallet_balance,uncleared_balance,wallet_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (rec.create_uid.id,rec.name,rec.private_key,rec.wallet_password,rec.wallet_balance,rec.uncleared_balance,rec.id))
                elif rec.id in db_id:
                    cur.execute('''select id,wallet_address from user_wallet where wallet_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.name != ids[0][1]:
                        cur.execute('''UPDATE user_wallet set wallet_address={} WHERE wallet_id={}'''.format(rec.name,rec.id))
            conn.commit()
            cur.close()
        except Exception as e:
            raise ValidationError(_(str(e)))
            

    