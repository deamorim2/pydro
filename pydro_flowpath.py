# Copyright (c) 2017 Gustavo S. F. Molleri (gustavo.molleri@gmail.com), Alexandre de Amorim Teixeira, (deamorim2@gmail.com)
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
#Python +2.0
#------------

#--------------------------
#VERSION 1.0 of 29/11/2017
#--------------------------

#--------------------------
#USAGE
#C:\DEM>python pydro_flowpath.py -d C:/DEM/ -s source.shp -i flowdirection.tif -o flowpath.tif -f t
#--------------------------

#----
#CODE

# Modulos utilizados
import os, sys, argparse
# from numpy import *
import numpy

from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst

#COMMAND-LINE PARSING

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--directory", action="store", dest="dir_name", help="Directory Name")
parser.add_argument("-s", "--source_points", action="store", dest="shp_name", help="Source Points Shapefile Name")
parser.add_argument("-i", "--input_flow_direction", action="store", dest="infile_name", help="Flow Direction File Name")
parser.add_argument("-o", "--output_flow_path_file", action="store", dest="outfile_name", help="Flow Path Output File Name")
parser.add_argument("-f", "--flow", action="store", dest="type_flow_direction", help="Type of Flow Direction: Taudem=t ArcGIS/TerraHydro=a", default='t')


args = parser.parse_args()

dir = args.dir_name
shp = args.shp_name
infile = args.infile_name
outfile = args.outfile_name
typeflow = args.type_flow_direction

#---------------------------------------------------------------------------------------------

class Stream():

	def __init__(self, dir, shp, infile, outfile):
		
		self.shp = shp	
		self.dir = dir
		self.infile = infile
		self.outfile = outfile
	
	
	#-------------------------------
	# OGR para extrair as coordenadas do .shp de nascentes
	def read_shp(self):

		ds = ogr.Open(self.shp,0)
		
		if ds is None:

			print "Open failed.\n"
			sys.exit(1)

		layer = self.shp.split('/')
		layer =  layer[-1][0:-4]

		lyr = ds.GetLayerByName(layer)
		
		# Identifica e salva a referencia espacial
		lyr.ResetReading()

		ptLst = []

		print '  Extraindo Vertices...'
		
		for feat in lyr:
			num_cod = feat.GetFieldAsDouble(0)
			geom = feat.GetGeometryRef()
			# print range(geom.GetPointCount())
			if geom == None:
				continue
				
			coord =[]

			for i in range(geom.GetPointCount()):
				
				x = '.'.join([str(geom.GetX(i)).split('.')[0],str(geom.GetX(i)).split('.')[1][:6]])
				y = '.'.join([str(geom.GetY(i)).split('.')[0],str(geom.GetY(i)).split('.')[1][:6]])
				
								
				coord.append([float(x),float(y)])
			
			
			if len(coord) == 0:
				continue				

			ptLst.append(coord[0])
			
			self.coord_nasc = ptLst


			
	#-------------------------------	
	# Abre a imagem e extrai informacoes	
	def raster(self):
	
		fname = self.infile

		# Abre o arquivo RASTER
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)
		
		if dataset is None:
			print ' Nao pode abrir o arquivo especificado! '
			sys.exit(1)
			
		print
		print '- Informacoes da IMAGEM'
		print '  Arquivo de imagem: ',fname
		
		# Adquire informacoes da Imagem
		print
		print '  Tipo de arquivo: ', dataset.GetDriver().ShortName,'/', \
			  dataset.GetDriver().LongName
		print
		
		self.ncol =  dataset.RasterXSize
		self.nlin =  dataset.RasterYSize
				
		print '  Dimensoes: '
		print '      ', dataset.RasterCount,' Banda(s)'
		print '      ', self.ncol,' Colunas'
		print '      ', self.nlin,' Linhas '
		print
		print '  Projecao da imagem: ',dataset.GetProjection()
		print


		driver = dataset.GetDriver()
		self.proj = dataset.GetProjection()
		self.geotransform = dataset.GetGeoTransform()

		
		self.originX = self.geotransform[0]
		self.originY = self.geotransform[3]
		self.pixelWidth = self.geotransform[1]
		self.pixelHeight = self.geotransform[5]
		
		print '  Coordenadas da origem = (',self.originX, ',',self.originY,')'
		print '  Dimensoes do pixel = (',self.pixelWidth, ',',self.pixelHeight,')'
		print

		# Adquire informacoes das bandas
		print '   Informacoes por BANDA'
		print
		
		band = dataset.GetRasterBand(1)

		type = gdal.GetDataTypeName(band.DataType)	
		print '  Caract. do dado =',type

		min = band.GetMinimum()
		max = band.GetMaximum()
		
		if min is None or max is None:
			(min,max) = band.ComputeRasterMinMax(1)
			
		print '  Min=%.3f, Max=%.3f' % (min,max)
		print
		
		print "- Carregando imagem p/ memoria..."
		self.data = band.ReadAsArray(0, 0, self.ncol, self.nlin)
	
	
	
	#-------------------------------
	# Cria matriz com informacao do fluxo		
	def matriz(self):
		# print "\n- Criando matriz ...\n"
		self.matriz = numpy.zeros((self.nlin,self.ncol), dtype=numpy.int)		

	
		
	#-------------------------------
	# Extrai o valor do pixel na imagem	
	def get_value(self):

		# Abre o arquivo RASTER	
		# PIL
		try:
			valor = self.data[self.ind_dir[0], self.ind_dir[1]]
			self.mat_value = self.matriz[self.ind_dir[0], self.ind_dir[1]]
			
			
		except:
			valor = -1
		# Numpy
		# valor = self.data[y_off,x_off]
		self.value = valor

	
	
	#-------------------------------
	# Identifica o indice do pixel na imagem 
	#	com base nas coordenadas do ponto
	def pixval(self,x,y):		

		# print 's',x, y 
		x_off = int((x - self.originX) / self.pixelWidth)
		y_off = int((y - self.originY) / self.pixelHeight)
				

		self.indice = [y_off,x_off]
		
		
		self.value = self.data[y_off,x_off]
		print "Pixel Nascente:  ",self.indice, self.value
		# exit()
		

		self.mat_value = self.matriz[y_off,x_off]
		
		print
	
	
	
	#-------------------------------
	# Identifica o pixel para onde o fluxo vai [col,lin]
	def direc(self):

		if typeflow == 't':

			if self.value == 1:
				ind_dir = [self.indice[0],self.indice[1]+1]
			elif self.value == 2:
				ind_dir = [(self.indice[0]-1),(self.indice[1]+1)]		
			elif self.value == 3:
				ind_dir = [(self.indice[0]-1),(self.indice[1])]
			elif self.value == 4:
				ind_dir = [(self.indice[0]-1),(self.indice[1]-1)]
			elif self.value == 5:
				ind_dir = [(self.indice[0]),(self.indice[1]-1)]
			elif self.value == 6:
				ind_dir = [(self.indice[0]+1),(self.indice[1]-1)]
			elif self.value == 7:
				ind_dir = [(self.indice[0]+1),(self.indice[1])]	
			elif self.value == 8:
				ind_dir = [(self.indice[0]+1),(self.indice[1]+1)]

		# Indice do pixel para onde o fluxo passa
			self.ind_dir = [ind_dir[0],ind_dir[1]]

		elif typeflow == 'a':
		
			if self.value == 1:
				ind_dir = [self.indice[0],self.indice[1]+1]
			elif self.value == 128:
				ind_dir = [(self.indice[0]-1),(self.indice[1]+1)]		
			elif self.value == 64:
				ind_dir = [(self.indice[0]-1),(self.indice[1])]
			elif self.value == 32:
				ind_dir = [(self.indice[0]-1),(self.indice[1]-1)]
			elif self.value == 16:
				ind_dir = [(self.indice[0]),(self.indice[1]-1)]
			elif self.value == 8:
				ind_dir = [(self.indice[0]+1),(self.indice[1]-1)]
			elif self.value == 4:
				ind_dir = [(self.indice[0]+1),(self.indice[1])]	
			elif self.value == 2:
				ind_dir = [(self.indice[0]+1),(self.indice[1]+1)]
		
		# Indice do pixel para onde o fluxo passa
			self.ind_dir = [ind_dir[0],ind_dir[1]]
		
	#-------------------------------
	# Calcula a direcao do fluxo 
	def fluxo(self):
	
		self.read_shp()
		self.raster()
		self.matriz()
		
		print '\n- Processando fluxo ...\n'
		
		# Apresenta as informacoes da imagem (RASTER)

		# Variaval onde serao armazenados os indices do fluxo

		# Contador
		b = 0
		print '\n Nascentes:\n'
		for x, y in self.coord_nasc:

			# Apresenta informacoes do processamento
			b = b + 1	
			
			print '  '+str(b)+'/'+str(len(self.coord_nasc))	
			
			# Chama a funcao pixval
			try:
				self.pixval(x,y)
			
			except:
				continue
			
			if self.value <= 0 or self.value == 255 or self.mat_value == 1:			
				continue
			
			# Insere na var temporaria 'collin' o indice referente as nascentes	
			collin = []
			collin = [[self.indice[0],self.indice[1]]]	
			
			self.matriz[self.indice[0], self.indice[1]] = 1
			
			a = 1		
		
			while a != 0:
				
				# Roda a funcao para identificar o indice do pixel
				#	para o onde o fluxo vai		
				self.direc()		
					
				if len(collin) <= 2:
				
					# collin = [[self.indice[0],self.indice[1]]]
					
					collin.append(self.ind_dir)
					
					self.matriz[self.ind_dir[0], self.ind_dir[1]] = 1
					
					self.indice = self.ind_dir
					
					self.get_value()					
					
					continue					
					
				self.get_value()
				
				if self.value <= 0 or self.value == 255 or self.mat_value == 1:	
					a = 0 
					continue
					
				collin.append(self.ind_dir)
				
				self.matriz[self.ind_dir[0], self.ind_dir[1]] = 1
				
				self.indice = self.ind_dir
			
			
		self.pix = None	
		
		self.salva_tif()
		
		
	
	#-------------------------------
	# Salva a imagem de saida em tif		
	def salva_tif(self):	
		print
		print " - Criando imagem de saida..."
		
		out_fname = self.dir+'/'+self.outfile
		
		print out_fname
		
		format = 'GTiff'

		out_driver = gdal.GetDriverByName(format)
		outDataset = out_driver.Create(out_fname, self.ncol, self.nlin, 1)
										
		
		outDataset.GetRasterBand(1).WriteArray(self.matriz, 0, 0)	


		outDataset.SetGeoTransform(self.geotransform)
		outDataset.SetProjection(self.proj)
		outDataset.GetRasterBand(1).GetStatistics(0,1)	
		
		outDataset = None
		out_driver = None
		
#-------------------------------		

# Executa a classe		

img = Stream(dir, shp, infile, outfile)

# Chama as funcoes

img.fluxo()
