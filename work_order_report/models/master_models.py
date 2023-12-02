from odoo import models,fields

class Moc(models.Model):
    _name = "moc"
    _description = "MOC"
    _rec_name = 'moc'

    moc = fields.Char("MOC")


class StemMoc(models.Model):
    _name = "stem.moc"
    _description = "Stem MOC"
    _rec_name = 'stem_moc'

    stem_moc = fields.Char("Stem MOC")

class FloatMoc(models.Model):
    _name = "float.moc"
    _description = "Float MOC"
    _rec_name = 'float_moc'

    float_moc = fields.Char("Float MOC")

class FlangeMoc(models.Model):
    _name = "flange.moc"
    _description = "Flange MOC"
    _rec_name = 'flange_moc'

    flange_moc = fields.Char("Flange MOC")

class FastenersMoc(models.Model):
    _name = "fasteners.moc"
    _description = "Fasteners MOC"
    _rec_name = 'fasteners_moc'

    fasteners_moc = fields.Char("Fasteners MOC")

class AdaptorMoc(models.Model):
    _name = "adaptor.moc"
    _description = "Adaptor MOC"
    _rec_name = 'adaptor_moc'

    adaptor_moc = fields.Char("Adaptor MOC")

class StemDia(models.Model):
    _name = "stem.dia"
    _description = "Stem Dia"
    _rec_name = 'stem_dia'

    stem_dia = fields.Char("Stem Dia")

class GasketMoc(models.Model):
    _name = "gasket.moc"
    _description = "Gasket MOC"
    _rec_name = 'gasket_moc'

    gasket_moc = fields.Char("Gasket MOC")

class ChamberMoc(models.Model):
    _name = "chamber.moc"
    _description = "Chamber MOC"
    _rec_name = 'chamber_moc'

    chamber_moc = fields.Char("Chamber MOC")

class WettedMoc(models.Model):
    _name = "wetted.moc"
    _description = "All Wetted Parts MOC"
    _rec_name = 'wetted_moc'

    wetted_moc = fields.Char("All Wetted Parts MOC")


class PackingDetails(models.Model):
    _name = "packing.details"
    _description = "Packing Details"
    _rec_name = 'packing_details'

    packing_details = fields.Char("Packing Details")

class MountType(models.Model):
    _name = "mount.type"
    _description = "Mount Type"
    _rec_name = 'mount_type'

    mount_type = fields.Char("Mount Type")

class ConnectionType(models.Model):
    _name = "connection.type"
    _description = "Connection Type"
    _rec_name = 'connection_type'

    connection_type = fields.Char("Connection Type")

class Connector(models.Model):
    _name = "connector"
    _description = "Connector"
    _rec_name = 'connector'

    connector = fields.Char("Connector")

class ConnectorVFS(models.Model):
    _name = "connector.vfs"
    _description = "Connector VFS"
    _rec_name = 'connector_vfs'

    connector_vfs = fields.Char("Connector VFS")

class ConnectorFLX(models.Model):
    _name = "connector.flx"
    _description = "Connector FLX"
    _rec_name = 'connector_flx'

    connector_flx = fields.Char("Connector FLX")


class Enclosure(models.Model):
    _name = "enclosure"
    _description = "Enclosure"
    _rec_name = 'enclosure'

    enclosure = fields.Char("Enclosure")

class Insulation(models.Model):
    _name = "insulation"
    _description = "Insulation Sleeving"
    _rec_name = 'insulation'

    insulation = fields.Char("Insulation Sleeving")


class Vent(models.Model):
    _name = "vent"
    _description = "Vent Type"
    _rec_name = 'vent'

    vent = fields.Char("Vent")

class Drain(models.Model):
    _name = "drain"
    _description = "Drain Type"
    _rec_name = 'drain'

    drain = fields.Char("Drain")


class Potting(models.Model):
    _name = "potting"
    _description = "Potting"
    _rec_name = 'potting'

    potting = fields.Char("Potting")

class MagneticSwitches(models.Model):
    _name = "magnetic.switches"
    _description = "Magnetic Switches"
    _rec_name = 'magnetic_switches'

    magnetic_switches = fields.Char("Magnetic Switches")

class LevelTransmitter(models.Model):
    _name = "level.transmitter"
    _description = "LevelTransmitter"
    _rec_name = 'level_transmitter'

    level_transmitter = fields.Char("Level Transmitter")

class ChamberFlangeType(models.Model):
    _name = "chamber.flange.type"
    _description = "Chamber Flange Type"
    _rec_name = 'chamber_flange_type'

    chamber_flange_type = fields.Char("Chamber Flange Type")

class ProcessPipeSize(models.Model):
    _name = "process.pipe.size"
    _description = "Process Conn. Pipe Size"
    _rec_name = 'process_pipe_size'

    process_pipe_size = fields.Char("Process Conn. Pipe Size")


class ProcessConnection(models.Model):
    _name = "process.connection"
    _description = "Process Connection"
    _rec_name = 'process_connection'

    process_connection = fields.Char("Process Connection")

class ProcessFlangeRating(models.Model):
    _name = "process.flange.rating"
    _description = "Process Flange Rating"
    _rec_name = 'process_flange_rating'

    process_flange_rating = fields.Char("Process Flange Rating")





