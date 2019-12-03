# Copyright (c) 2019 Gustavo S. F. Molleri (gustavo.molleri@gmail.com), Alexandre de Amorim Teixeira, (deamorim2@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General pghydro License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General pghydro License for more details.
#
# You should have received a copy of the GNU General pghydro License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

#------------
#REQUIREMENTS
#Python 2.7.5+
#GDAL 2.1.2+
#QGIS 2.x
#------------

#--------------------------
#VERSION 1.2 of 03/12/2019
#--------------------------

#--------------------------
#USAGE
#python pydro_agreedem_gdal.py -w C:/workspace/ -hy C:/workspace/tdr.shp -i C:/workspace/img02.tif -o C:/workspace/agreedem.tif -bf 2 -sm 5 -sh 100 -gd "C:/Program Files/QGIS 2.18/bin" -od "C:/Program Files/QGIS 2.18/bin"
#--------------------------

#--------------------------
#REFERENCE
#http://www.ce.utexas.edu/prof/maidment/gishydro/ferdi/research/agree/agree.html
#

#----
#CODE


#----------------------------------------------------------------------------------
# Modulos utilizados
import os, argparse
import shutil
import time

#COMMAND-LINE PARSING

parser = argparse.ArgumentParser()

parser.add_argument("-w", "--directory workspace", action="store", dest="dir_name", help="Workspace Directory")
parser.add_argument("-hy", "--hydrography", action="store", dest="shp_name", help="Hydrography Shapefile Name Directory")
parser.add_argument("-i", "--input_dem_file", action="store", dest="infile_name", help="DEM File Name Directory")
parser.add_argument("-o", "--agreedem", action="store", dest="agreedem_file_name", help="Agreedem File Name")
parser.add_argument("-bf", "--buffer", action="store", dest="buffer_value", type=int, help="Buffer distance in Pixel")
parser.add_argument("-sm", "--smooth", action="store", dest="smooth_value", type=int, help="Smooth modified elevation")
parser.add_argument("-sh", "--sharp", action="store", dest="sharp_value", type=int, help="Sharp drop/raise grid")
parser.add_argument("-gd", "--gdal_directory", action="store", dest="gdal_directory", help="Gdal Directory Name")
parser.add_argument("-od", "--osgeo_directory", action="store", dest="osgeo_directory", help="OSGEO Directory Name")

args = parser.parse_args()

default_dir = args.dir_name
srtm_filename = args.infile_name
shp_dir = args.shp_name
shp_hidro = args.shp_name
buf_dist_pixels = args.buffer_value
input_smooth = args.smooth_value
input_sharp = args.sharp_value
agreedem = args.agreedem_file_name

gdal_dir = args.gdal_directory
osgeo_dir = args.osgeo_directory

# ----------------------------------------------
class ProcessaAgreeDEM():
	"""
	Reference:
		http://www.ce.utexas.edu/prof/maidment/gishydro/ferdi/research/agree/agree.html
	"""
	def __init__(self, gdal_path, osgeo_path, proc_dir, srtm_file, hidro_shp, dist_pixels, smooth, sharp):
		self.gdal_dir =gdal_path
		self.osgeo_dir =osgeo_path
		self.proc_dir = proc_dir
		self.srtm = srtm_file
		self.hidro = hidro_shp
		self.dist_pixels = dist_pixels
		self.smooth_drop = smooth
		self.sharp_drop = sharp
		self.vectgrid = os.path.join(self.proc_dir, 'vectgrid.tif')
		self.vectallo = os.path.join(self.proc_dir, 'vectallo.tif')
		self.vectdist = os.path.join(self.proc_dir, 'vectdist.tif')
		self.bufgrid = os.path.join(self.proc_dir, 'bufgrid.tif')
		self.agree = agreedem


	# ------------------------
	def executa_Proc(self):

		inicio_proc = time.time()
		self.calc_Vectgrid()
		self.calc_Vectallo()
		self.calc_Vectdist()
		self.calc_Bufgrid()
		self.calc_Agree()
		self.tempo_Processamento(inicio_proc)


	# ------------------------
	def tempo_Processamento(self, start):
		end = time.time()

		elapsed = end - start

		# Para converter em minutos
		minutos = elapsed / 60
		hora = minutos / 60
		min = (hora - int(hora)) * 60

		print "\n\n-> Tempo de processamento: ", int(hora), ":h ", min, ":min"


	# ------------------------
	def generate_TempRaster(self):
		self.empty_raster = os.path.join(self.proc_dir, 'empty_raster.tif')
		self.calcula_1Raster(self.srtm, self.empty_raster, 'Int32', "A*0")

	# ------------------------
	def delete_Raster(self, temp):
		os.remove(temp)


	# ------------------------
	def calcula_1Raster(self, input_img, output_img, output_format, equation):
		"""
		Reference:
			http://www.gdal.org/gdal_calc.html
		"""
		os.chdir(self.gdal_dir)

		cmd = """python gdal_calc.py -A %s --type=%s --outfile=%s --calc %s """%(input_img, output_format, output_img, equation)
		print '\n\t\t-Calculando 1 raster:'
		print '\t\t\tArquivo Entrada : (A)', input_img
		print '\t\t\tEquacao: ',equation
		print '\t\t\tArquivo Saida: ', output_img
		print '\t\t\tComando: ', cmd
		os.system(cmd)


	# ------------------------
	def calcula_2Raster(self, input_img1, input_img2, output_img, output_format, equation, nodata_value=''):
		"""
		Reference:
			http://www.gdal.org/gdal_calc.html
			{Byte/Int16/UInt16/UInt32/Int32/Float32/Float64/CInt16/CInt32/CFloat32/CFloat64}
		"""
		os.chdir(self.gdal_dir)
		if nodata_value != '':
			nodata_value = """--NoDataValue=%s"""%(nodata_value)

		cmd = """python gdal_calc.py -A %s -B %s --type=%s --outfile=%s --calc %s %s"""%(input_img1, input_img2, output_format, output_img, equation, nodata_value)
		print '\n\t\t-Calculando 2 raster:'
		print '\t\t\tArquivos Entrada : \n\t\t\t\t(A)', input_img1, '\n\t\t\t\t(B)',input_img2
		print '\t\t\tEquacao: ',equation
		print '\t\t\tArquivo Saida: ', output_img
		print '\t\t\tComando: ', cmd
		os.system(cmd)


	# ------------------------
	def calc_Vectgrid(self):
		"""
		- Converte a hidrografia em raster;

		- Reference:
			http://www.gdal.org/gdal_rasterize.html
		"""
		cmd = """gdal_rasterize -burn 1 -at %s %s""" % (self.hidro, self.vectgrid)
		print '\n------------------------------------------------------------'
		print '->Calculando Vectgrid:'
		print '\tArquivo Entrada: ', self.hidro
		print '\tArquivo Saida: ', self.vectgrid
		print '\tComando:\n\t', cmd

		self.generate_TempRaster()
		shutil.copyfile(self.empty_raster, self.vectgrid)
		os.chdir(self.osgeo_dir)
		os.system(cmd)


	# ------------------------
	def calc_Vectallo(self):
		"""
		- Extrai os valores do SRTM para os valores da hidrografia resterizada;

		- Reference:
			http://www.gdal.org/gdal_proximity.html
		"""
		print '\n------------------------------------------------------------'
		print '->Calculando Vectallo:'
		print '\tArquivo Entrada: ', self.vectgrid
		print '\tArquivo Saida: ',  self.vectallo

		equation = """A*B"""
		self.calcula_2Raster(self.srtm, self.vectgrid, self.vectallo, 'Int32', equation)


	# ------------------------
	def calc_Vectdist(self):
		"""
		- Calcula a distancia em pixels da hidrografia rasterizada ate uma determinada distancia "self.dist_pixels";

		- Reference:
			http://www.gdal.org/gdal_proximity.html
		"""

		vectdist_temp = os.path.join(self.proc_dir, 'vectdist_temp.tif')

		shutil.copyfile(self.empty_raster, vectdist_temp)

		os.chdir(self.gdal_dir)
		cmd = """python gdal_proximity.py %s %s -ot Int32 -values 1 -distunits PIXEL -maxdist %s -nodata 0"""%(self.vectgrid, vectdist_temp, self.dist_pixels + 1)
		print '\n------------------------------------------------------------'
		print '->Calculando Vectdist:'
		print '\tArquivo Entrada: ', self.vectgrid
		print '\tArquivo Saida: ',  self.vectdist
		print '\tComando:\n\t', cmd
		os.system(cmd)

		equation = """(-%s+A)*%s"""%(self.dist_pixels + 1, self.smooth_drop)
		self.calcula_1Raster(vectdist_temp, self.vectdist, 'Int32', equation)
		self.delete_Raster(vectdist_temp)


	# ------------------------
	def calc_Bufgrid(self):
		"""
		- Buffer da hidrografia com base em uma distancia em pixels;

		- Reference:
			http://www.gdal.org/gdal_proximity.html
		"""
		os.chdir(self.gdal_dir)
		cmd = """python gdal_proximity.py %s %s -ot Int32 -values 1 -distunits PIXEL -maxdist %s -fixed-buf-val 1 -nodata 0"""%(self.vectgrid, self.bufgrid, self.dist_pixels)
		print '\n------------------------------------------------------------'
		print '->Calculando Bufgrid:'
		print '\tArquivo Entrada: ', self.vectgrid
		print '\tArquivo Saida: ',  self.bufgrid
		print '\tComando:\n\t', cmd
		os.system(cmd)


	# ------------------------
	def calc_Agree(self):
		"""

		- Reference:

		"""
		print '\n------------------------------------------------------------'
		print '->Calculando AgreeDem:'
		print '\tArquivo Entrada: ', self.srtm
		print '\tArquivo Saida: ', self.agree

		print '\n\tPasso 1: '
		agree_temp1 = os.path.join(self.proc_dir, 'agree_temp1.tif')
		self.calcula_2Raster(self.vectdist, self.bufgrid, agree_temp1, 'Int32', "A*B")

		print '\n\tPasso 2: '
		agree_temp2 = os.path.join(self.proc_dir, 'agree_temp2.tif')
		equation = """A*(-%s)"""% (self.sharp_drop)
		self.calcula_1Raster(self.vectgrid, agree_temp2, 'Int32', equation)

		print '\n\tPasso 3: '
		agree_temp3 = os.path.join(self.proc_dir, 'agree_temp3.tif')
		self.calcula_2Raster(agree_temp1, agree_temp2, agree_temp3, 'Int32', "A+B")

		print '\n\tPasso 4 (FINAL): '
		self.calcula_2Raster(self.srtm, agree_temp3, self.agree, 'Int32', "A+B", -32768)

		self.delete_Raster(agree_temp1)
		self.delete_Raster(agree_temp2)
		self.delete_Raster(agree_temp3)

# Executa processo
p = ProcessaAgreeDEM(gdal_dir, osgeo_dir, default_dir, srtm_filename, shp_hidro, buf_dist_pixels, input_smooth, input_sharp)
p.executa_Proc()

print "   FIM DO PROGRAMA   "

