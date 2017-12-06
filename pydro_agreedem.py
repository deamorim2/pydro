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
#Python 2.7.5+
#GDAL 2.1.2+
#------------

#--------------------------
#VERSION 1.0 of 01/12/2017
#--------------------------

#--------------------------
#USAGE
#C:\workspace>python pydro_agreedem.py -w C:/workspace/ -hy C:/workspace/tdr.shp -i C:/workspace/img02.tif -o agreedem -bf 2 -sm 5 -sh 100
#--------------------------

#--------------------------
#REFERENCE
#http://www.ce.utexas.edu/prof/maidment/gishydro/ferdi/research/agree/agree.html
#

#----
#CODE

# Modulos utilizados
import os, sys, argparse
import numpy
from osgeo import gdal
from osgeo import ogr
from osgeo import gdalconst

#COMMAND-LINE PARSING

parser = argparse.ArgumentParser()

parser.add_argument("-w", "--directory workspace", action="store", dest="dir_name", help="Workspace Directory")
parser.add_argument("-hy", "--hydrography", action="store", dest="shp_name", help="Hydrography Shapefile Name Directory")
parser.add_argument("-i", "--input_dem_file", action="store", dest="infile_name", help="DEM File Name Directory")
parser.add_argument("-o", "--output_agreedem_file_name", action="store", dest="outfile_name", help="Output AgreeDEM File Name")
parser.add_argument("-bf", "--buffer", action="store", dest="buffer_value", type=int, help="Buffer distance in Pixel")
parser.add_argument("-sm", "--smooth", action="store", dest="smooth_value", type=int, help="Smooth modified elevation")
parser.add_argument("-sh", "--sharp", action="store", dest="sharp_value", type=int, help="Sharp drop/raise grid")

args = parser.parse_args()

dir = args.dir_name
hidro = args.shp_name
dem = args.infile_name
agreeDEM = args.outfile_name
tam_buf = args.buffer_value
smooth = args.smooth_value
sharp = args.sharp_value

#----------------------------------------------------------------------------------	

class agree_dem():
    
            	
	def __init__(self, dir_agree, hidro, dem, out_agree,
					tam_buf,
					smooth,
					sharp):
		
            		
		self.dir = dir_agree	
		self.hidro = hidro	
		self.dem_file = dem
		self.out_agree = out_agree		
		self.tam = tam_buf
		self.smooth = smooth
		self.sharp = sharp
	
	
	#-------------------------------	
	# Cria um raster com base no .shp da hidrografia		
	def abre_dem(self):

	
		fname = self.dem_file

		# Abre o arquivo RASTER
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)

		if dataset is None:
			print ' Nao pode abrir o arquivo especificado! '
			sys.exit(1)
			
		print '\n\n#-------------------------------'
		print '- Informacoes da IMAGEM de referencia'
		print '  Arquivo de imagem: ',fname

		# Adquire informacoes da Imagem
		print
		print '  Tipo de arquivo: ', dataset.GetDriver().ShortName,'/', \
			  dataset.GetDriver().LongName
		print

		self.ncol =  dataset.RasterXSize
		self.nlin =  dataset.RasterYSize
				
		print '  Dimensoes: '
		print '      ', dataset.RasterCount, ' Banda(s)'
		print '      ', self.ncol, ' Colunas'
		print '      ', self.nlin, ' Linhas '
		print
		print '  Projecao da imagem: ', dataset.GetProjection()
		print


		driver = dataset.GetDriver()
		self.proj = dataset.GetProjection()
		self.geotransform = dataset.GetGeoTransform()

		originX = self.geotransform[0]
		originY = self.geotransform[3]
		pixelWidth = self.geotransform[1]
		pixelHeight = self.geotransform[5]

		print '  Coordenadas da origem = (',originX, ',',originY,')'
		print '  Dimensoes do pixel = (',pixelWidth, ',',pixelHeight,')'
		print

		# Adquire informacoes das bandas
		print '   Informacoes por BANDA'
		print

		band = dataset.GetRasterBand(1)

		self.type = gdal.GetDataTypeName(band.DataType)	
		print '  Caract. do dado =',self.type

		min = band.GetMinimum()
		max = band.GetMaximum()

		if min is None or max is None:
			(min,max) = band.ComputeRasterMinMax(1)
			
		print '  Min=%.3f, Max=%.3f' % (min,max)
		print

		fname = None
		dataset = None
		band = None			


	#-------------------------------	
	# Cria um raster com base no .shp da hidrografia		
	def rasterize(self):
	
		print '\n\n#-------------------------------'
		print '  Rasterizando hidrografia ... \n'	

		fname = self.dir+'hidro_raster.tif'
		target_ds = gdal.GetDriverByName('GTiff').Create(self.dir+'hidro_raster.tif',
															self.ncol,
															self.nlin,
															gdal.GDT_Byte)
		
		
		target_ds.SetGeoTransform(self.geotransform)
		
		# Create a layer to rasterize from.
		shp = self.hidro
		
		ds = ogr.Open(shp)
			
		layer = shp.split('/')
		layer =  layer[-1][0:-4]

		lyr = ds.GetLayerByName(layer)		

		# Run the algorithm.
		err = gdal.RasterizeLayer(target_ds,
									[1],
									lyr,
									burn_values=[1],
									options =["ALL_TOUCHED=TRUE"])#,
									# options=["VALUE=%f" % 1])
									
		target_ds.GetRasterBand(1).GetStatistics(0,1)
		
		print '\n  Salvando imagem ... \n'
		print '    Arquivo gerado: '+fname
		
		target_ds = None
		
		
	#-------------------------------	
	# Cria um buffer no raster de hidro		
	def f_bufdist(self):
	
		print '\n\n#-------------------------------'
		print '  Processando bufdist... \n'

		print '    Tamanho do buffer:',self.tam,'pixels'
		print '    Smooth:',self.smooth,'m'
		
		# Abre arquivos RASTER
		fname = self.dir+'hidro_raster.tif'
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		
		rio_raster = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#uint16
		bufdist = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#uint16		
		
		fname = None
		dataset = None
		band = None	
		
		mascara = numpy.zeros((self.nlin, self.ncol), dtype = 'int16')#uint16
		
		index = numpy.transpose(numpy.where(rio_raster == 1))
		
		for ind in index:			
		
			mask = range((self.tam*-1),(self.tam*1)+1)

			for lin in mask:

				for col in mask:
					
					linha = ind[0]-lin
					coluna = ind[1]-col			
					
					if linha > self.nlin - 1 or \
						coluna > self.ncol - 1 or \
						linha < 0 or coluna < 0:						
						continue						
					
					
					peso = max([abs(lin),abs(col)])						
					
					if bufdist[linha,coluna] < peso and bufdist[linha,coluna] != 0:
						continue		
					
					elif bufdist[linha,coluna] == 0 or bufdist[linha,coluna] > peso:

						bufdist[linha,coluna] = peso						
						bufdist[ind[0],ind[1]] = 1									
						
						mascara[linha,coluna] = 1	
						mascara[ind[0],ind[1]] = 1	
						
		
		bufdist = bufdist - rio_raster		
		bufdist = bufdist - (self.tam + 1)
		bufdist = numpy.negative(bufdist)
		bufdist = numpy.multiply(bufdist,mascara)
		bufdist = numpy.multiply(bufdist,self.smooth)
		bufdist.astype('int16')#uint16
		
			
		print '\n  Salvando imagem ... \n'
		out_fname = self.dir+'bufdist.tif'
		format = 'GTiff'		
		out_driver = gdal.GetDriverByName(format)
		outDataset = out_driver.Create(out_fname,
										self.ncol,
										self.nlin,
										1,
										gdal.GDT_Int16)#UInt16	
		outDataset.GetRasterBand(1).WriteArray(bufdist, 0, 0)	
		outDataset.SetGeoTransform(self.geotransform)
		outDataset.GetRasterBand(1).GetStatistics(0,1)
		print '    Arquivo gerado: '+out_fname		
		
		
		print '\n  Salvando imagem ... \n'
		out_fname = self.dir+'mascara.tif'	
		format = 'GTiff'		
		out_driver = gdal.GetDriverByName(format)
		outDataset = out_driver.Create(out_fname,
										self.ncol,
										self.nlin,
										1,
										gdal.GDT_Int16)#UInt16	
		outDataset.GetRasterBand(1).WriteArray(mascara, 0, 0)	
		outDataset.SetGeoTransform(self.geotransform)
		#outDataset.SetProjection(self.proj)
		outDataset.GetRasterBand(1).GetStatistics(0,1)
		print '    Arquivo gerado: '+out_fname
		
		
		dataset = None
		band = None	
		outDataset = None
		out_driver = None

		
	#-------------------------------	
	# Insere os valores mais proximos dentro do buffer	
	def f_bufallo(self):
		
		print '\n\n#-------------------------------'
		print '  Processando bufallo ... \n'
		
		# Abre arquivos RASTER
		# dem
		fname = self.dem_file
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		dem = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#uint16		
		
		# Hidrografia
		fname = self.dir + 'hidro_raster.tif'
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		rio_raster = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#uint16		
		
		# Bufdist		
		fname = self.dir + 'bufdist.tif'
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		bufdist = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#uint16		
		
		fname = None
		dataset = None
		band = None			
		
		bufallo = numpy.zeros((self.nlin, self.ncol), dtype = 'int16')#float32	
				
		# Identifica o indice do rio
		# ind_rio = numpy.where(bufdist != 0)		
		ind_rio = numpy.transpose(numpy.where(bufdist != 0))
		k = 1
		for ind in ind_rio:
			
			print k,'/',len(ind_rio)
			k = k+1	
			
			if dem[ind[0],ind[1]] == 0:				
				continue
				
			# Constroi janela 
			jan_lin = range((ind[0] - (self.tam + 2)),(ind[0] + (self.tam + 3)))
			jan_col = range((ind[1] - (self.tam + 2)),(ind[1] + (self.tam + 3)))

			jan = []
			jan_value = []			
			guard = []
			guard_value = []
			guard_bufd = []	
			
			for l in jan_lin:
			
				for c in jan_col:	
				
					if l > self.nlin - 1 or \
						c > self.ncol - 1 or \
						l < 0 or c < 0:							
						continue		
							
					if rio_raster[l,c] == 1 or \
						dem[l,c] == 0:			
						continue	
						
					elif bufdist[l,c] != 0:
						guard.append([l,c])
						guard_value.append(dem[l,c])
						guard_bufd.append(bufdist[l,c])
						continue	
						
					elif bufdist[l,c] == 0:	
						jan.append([l,c])
						jan_value.append(dem[l,c])	
						continue			

			
			# Nas bifurcacoes, caso nao haja valor proximo utilize o valor do dem 
			# da maior distancia dentro do bufferdist	
			if len(jan_value) == 0:				

				guard_ind = [] 
				guard_val = []			
				for n in range(len(guard_bufd)):

					if guard_bufd[n] == min(guard_bufd):
						guard_ind.append(guard[n])	
						guard_val.append(guard_value[n])

				
				if len(guard_ind) == 0:
					continue
					
				index = guard_ind				
				valor = guard_val


			else:
				index = jan
				valor = jan_value
				
			
			dist = []
			
			xya = [ind[0],ind[1]]

			
			for j in index:	
				
				xyb = [j[0],j[1]]			

				calc = numpy.sqrt((xya[0]-xyb[0]) ** 2 + (xya[1]-xyb[1]) ** 2)
				
				dist.append(calc)
			

			# Indice das distancias minimas
			ind_min = numpy.where(dist == min(dist))
						
			val = []
			
			for n in ind_min[0]:
			
				val.append(valor[n])	

				
			# Insere o valor na matriz de mascara	
			bufallo[ind[0],ind[1]] = numpy.mean(val)
				

		del rio_raster, dem
		
		
		print '\n  Salvando imagem ... \n'
		out_fname = self.dir+'bufallo.tif'
		format = 'GTiff'		
		out_driver = gdal.GetDriverByName(format)
		outDataset = out_driver.Create(out_fname,
										self.ncol,
										self.nlin,
										1,
										gdal.GDT_Int16)#Float32	
		outDataset.GetRasterBand(1).WriteArray(bufallo, 0, 0)	
		outDataset.SetGeoTransform(self.geotransform)
		outDataset.GetRasterBand(1).GetStatistics(0,1)
		print '    Arquivo gerado: '+out_fname
		
		outDataset = None
		out_driver = None
	
	
	#-------------------------------	
	# Extrai o vectgrid	
	def f_vectgrid(self):	
	
		print '\n\n#-------------------------------'
		print '  Processando vectgrid ... \n'	
		
		# Abre arquivos RASTER
		# dem
		fname = self.dem_file
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		dem = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#uint16		
		
		# Hidrografia
		fname = self.dir + 'hidro_raster.tif'
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		rio_raster = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#uint16		
						
		fname = None
		dataset = None
		band = None	
		
		vectgrid = numpy.zeros((self.nlin,self.ncol), dtype = 'int16')#uint16			

		ind_rio = numpy.where(rio_raster == 1)		
			
		vectgrid[ind_rio] = dem[ind_rio]
		
		
		print '\n  Salvando imagem ... \n'
		out_fname = self.dir + 'vectgrid.tif'
		format = 'GTiff'		
		out_driver = gdal.GetDriverByName(format)
		outDataset = out_driver.Create(out_fname,
										self.ncol,
										self.nlin,
										1,
										gdal.GDT_Int16)#Float32	
		outDataset.GetRasterBand(1).WriteArray(vectgrid, 0, 0)	
		outDataset.SetGeoTransform(self.geotransform)
		outDataset.GetRasterBand(1).GetStatistics(0,1)
		print '    Arquivo gerado: '+out_fname
		
		outDataset = None
		out_driver = None	
	
	
	#-------------------------------	
	# Gera o DEM modificado		
	def f_agree(self):
	
		print '\n\n#-------------------------------'
		print '  Processando AgreeDEM ... '
				
		# Abre arquivos RASTER

		
		# Hidrografia
		fname = self.dir+'hidro_raster.tif'
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		hidro_raster = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#uint16		
						
		
		del dataset, band
		
		print '  Hidrografia ok! '
		
		# Bufallo		
		fname = self.dir+'bufallo.tif'
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		bufallo = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin),dtype = 'int16')#float32		
		
		del dataset, band
		
		hidro_raster_1 = hidro_raster - 1
		hidro_raster_1 = numpy.negative(hidro_raster_1)		
		
		hidro_raster_afun = numpy.multiply(hidro_raster,self.sharp)	
				
		bufallo = numpy.multiply(bufallo,hidro_raster_1)
		
		del hidro_raster_1,hidro_raster,self.sharp
		
		print '  Bufallo ok! '
		
		# Vectgrid		
		fname = self.dir+'vectgrid.tif'
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		vectgrid = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#float32		
		
		del dataset, band
		
		bufallo = bufallo + vectgrid
		
		del vectgrid
		
		print '  Vectgrid ok! '
		
		# Bufdist		
		fname = self.dir+'bufdist.tif'
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		bufdist = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin),dtype = 'int16')#float32		
		
		del dataset, band
		
		bufdist = numpy.negative(bufdist)		
		
		smoelev = bufallo + bufdist
		
		del bufallo, bufdist#, band, dataset
		
		shagrid = smoelev - hidro_raster_afun
		
		del hidro_raster_afun, smoelev

		# dem
		fname = self.dem_file
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		agree = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#float32		
		
		del dataset, band
		
		print '  dem ok! '
		
		# Mascara
		fname = self.dir + 'mascara.tif'	
		dataset = gdal.Open(fname, gdalconst.GA_ReadOnly)		
		band = dataset.GetRasterBand(1)
		mascara = numpy.array(band.ReadAsArray(0, 0, self.ncol, self.nlin), dtype = 'int16')#uint16		
		
		del dataset, band
		
		print '  Mascara ok! '
		
		# Calculos
		mascara = mascara - 1
		mascara = numpy.negative(mascara)
		
		agree = numpy.multiply(mascara,agree)

		print '  Calculo Efetuado! '
		
		# del
		
		del mascara
		
		print '  del ok! '
		
		agree = agree + shagrid
		
		del shagrid	

		print '  Bufdist ok! '
		
		print '\n  Salvando imagem ... \n'
		
		# Tiff
		print '\t.Tiff'
		out_fname = self.dir+self.out_agree+'.tif'
		format = 'GTiff'		
		out_driver = gdal.GetDriverByName(format)
		outDataset = out_driver.Create(out_fname,
										self.ncol,
										self.nlin,
										1,
										gdal.GDT_Int16)#Float32		
		
		outDataset.GetRasterBand(1).WriteArray(agree, 0, 0)
		outDataset.GetRasterBand(1).SetNoDataValue(-9999) 		
		outDataset.SetGeoTransform(self.geotransform)
		outDataset.GetRasterBand(1).GetStatistics(0,1)		
		print '    Arquivo gerado: '+out_fname		
		
	
#-------------------------------		
# Chama a classe
agree = agree_dem(dir, hidro, dem, agreeDEM,tam_buf,smooth,sharp)

# Executas as funcoes
agree.abre_dem()
agree.rasterize()
agree.f_bufdist()
agree.f_bufallo()
agree.f_vectgrid()
agree.f_agree()

#----------------------------------------------------------------------------------