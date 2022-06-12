#!/usr/bin/env python

import itertools
import argparse
from enum import Enum

import cadquery as cq


def in2mm(mm):
    return mm*25.4

def frange(start, stop=None, step=None):
    """
    range, except supports floating point numbers.
    """
    start = float(start)
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0

    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1


class HoleSize(Enum):
    small = in2mm(1/8)
    large = in2mm(1/4)
    
    def __str__(self):
        return self.value
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Programmatically generate a pegboard from input parameters.')
    parser.add_argument('width', type=float, 
                        help='Width of the pegboard in inches. For keeping the holes centered with the pegboard, make this a multiple of the hole distance.')
    parser.add_argument('height', type=float, 
                        help='Height of the pegboard in inches. For keeping the holes centered with the pegboard, make this a multiple of the hole distance.')
    parser.add_argument('filename', type=str,
                        help='Path to the output file. Th extension implies the output format.')
    parser.add_argument('--hole_diameter', '-d', type=float, default=1,
                        help='Diameter of the peg holes, "small" creates 1/8 inch holes. "large" create 1/4 inch holes.')
    parser.add_argument('--hole_spacing', '-s', type=float, default=1,
                        help='Distance between pegboard holes in inches.')
    parser.add_argument('--buffer', '-b', type=float, default=in2mm(1/4), 
                        help='Buffer between the edge of the pegboard and the holes.' )
    parser.add_argument('--fillet', '-f', type=float, default=in2mm(1/4), 
                        help='Fillet of the corners in inches' )
    parser.add_argument('--thickness', '-t', type=float, default=in2mm(1/8), 
                        help='Thickness of the board, only appplies to 3d output formats like STL.')
    
    

    args = parser.parse_args()
    
    hole_spacing = args.hole_spacing
    hole_diameter = args.hole_diameter
    
    width = in2mm(args.width)
    height = in2mm(args.height)
    thickness = in2mm(args.thickness)
    fillet = in2mm(args.fillet)
    buffer = in2mm(args.buffer)
    filename = args.filename
    nheight = height - buffer
    nwidth = width - buffer


    ypoints = frange(-nheight/2, nheight/2+1, hole_spacing)
    xpoints = frange(-nwidth/2, nwidth/2+1, hole_spacing)
    points = list(itertools.product(xpoints, ypoints))
    
    turtwig = (cq.Sketch()
                  .rect(width, height)
                  .vertices()
                  .fillet(fillet).reset()
                  .push(points)
                  .circle(hole_diameter, mode='s')
                  .clean().reset()
    )

    turtwig = cq.Workplane("XY").placeSketch(turtwig).extrude(thickness)
    cq.exporters.export(turtwig, filename)
