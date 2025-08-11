import numpy as np
import os
from collections import Counter
from pwdata.build.cell import cell_to_cellpar
from pwdata.calculators.const import elements, ELEMENTMASSTABLE


def write_config(image,
                 data_path,
                 data_name="toatom.config",
                 direct=True,
                 sort=None,
                 symbol_count=None,
                 long_format=True,
                 ignore_constraints=False,
                 wrap=False):
    """Method to write PWmat position (atom.config) files.

    Writes label, unitcell, # of various kinds of atoms,
    positions scaled coordinates (Direct), and constraints
    to file. fractional coordinates is default.
    """
    # assert direct==True, "PWmat only support direct coordinates"
    atom_nums = len(image) if image.atom_nums is None else image.atom_nums
    if isinstance(image, (list, tuple)):
        if atom_nums > 1:
            raise RuntimeError('Don\'t know how to save more than ' +
                               'one image to PWmat input')
        else:
            image = image[0]

    # Check lattice vectors are finite
    """Get unit cell parameters. Sequence of 6 numbers.

    First three are unit cell vector lengths and second three
    are angles between them::

        [len(a), len(b), len(c), angle(b,c), angle(a,c), angle(a,b)]

    in degrees.

    radians: bool, Convert angles to radians.

    See also :func:`cell.cell_to_cellpar`."""
    cellpar = cell_to_cellpar(image.lattice, radians = False)
    if np.any(cellpar == 0.):
        raise RuntimeError(
            'Lattice vectors must be finite and not coincident. '
            'At least one lattice length or angle is zero.')

    # Write atom positions in scaled coordinates. For PWmat, we must use fractional coordinates
    if image.cartesian:                                 # cartesian -> direct
        coord = image.get_scaled_positions(wrap=wrap)
    else:                                               # get direct
        coord = image.position

    '''constraints = image.constraints and not ignore_constraints

    if constraints:
        sflags = np.zeros((atom_nums, 3), dtype=bool)
        for constr in image.constraints:
            if isinstance(constr, FixScaled):
                sflags[constr.a] = constr.mask
            elif isinstance(constr, FixAtoms):
                sflags[constr.index] = [True, True, True]
            elif isinstance(constr, FixedPlane):
                mask = np.all(np.abs(np.cross(constr.dir, image.cell)) < 1e-5,
                              axis=1)
                if sum(mask) != 1:
                    raise RuntimeError(
                        'VASP requires that the direction of FixedPlane '
                        'constraints is parallel with one of the cell axis')
                sflags[constr.a] = mask
            elif isinstance(constr, FixedLine):
                mask = np.all(np.abs(np.cross(constr.dir, image.cell)) < 1e-5,
                              axis=1)
                if sum(mask) != 1:
                    raise RuntimeError(
                        'VASP requires that the direction of FixedLine '
                        'constraints is parallel with one of the cell axis')
                sflags[constr.a] = ~mask'''

    if sort:
        if len(image.get_atomic_numbers()) == 0:
            atom_types_image = np.array(image.atom_types_image)
            indices_dict = {type: np.where(atom_types_image == type)[0] for type in image.atom_type}
            sorted_indices = np.concatenate([np.sort(indices) for indices in indices_dict.values()])
            symbols = atom_types_image[sorted_indices]
        else:
            sorted_indices = np.argsort(image.get_atomic_numbers())
            symbols = np.array(image.get_atomic_numbers())[sorted_indices]
        coord = np.array(coord)[sorted_indices]
        # if constraints:
        #     sflags = sflags[ind]
    else:
        symbols = image.atom_types_image
    
    # Create a list sc of (symbol, count) pairs
    if symbol_count:
        # sc = symbol_count
        pass
    elif image.atom_type_num is None:
        sc = Counter(symbols)
        atom_type = list(sc.keys())
        atom_type_num = list(sc.values())
    else:
        atom_type = image.atom_type
        atom_type_num = image.atom_type_num

    # Write to file
    output_file = open(os.path.join(data_path, data_name), 'w')
    output_file.write('%d\n' % atom_nums)
    output_file.write('Lattice vector\n')
    for i in range(3):
        output_file.write('%19.16f %19.16f %19.16f\n' % tuple(image.lattice[i]))
    output_file.write(' Position, move_x, mov_y, move_z\n')
    for i in range(atom_nums):
        output_file.write('%4d %19.16f %19.16f %19.16f %2d %2d %2d\n' %
                          (symbols[i], coord[i][0], coord[i][1], coord[i][2],
                           1, 1, 1))
    output_file.close()
    print("Convert to %s successfully!" % data_name)
    
def write_vasp(image,
               data_path,
               data_name="vasp.poscar",
               direct=False,
               sort=None,
               symbol_count=None,
               long_format=True,
               vasp5=True,
               ignore_constraints=False,
               wrap=False):
    """Method to write VASP position (POSCAR/CONTCAR) files.

    Writes label, scalefactor, unitcell, # of various kinds of atoms,
    positions in cartesian or scaled coordinates (Direct), and constraints
    to file. Cartesian coordinates is default and default label is the
    atomic species, e.g. 'C N H Cu'.
    """
    atom_nums = len(image) if image.atom_nums is None else image.atom_nums
    if isinstance(image, (list, tuple)):
        if atom_nums > 1:
            raise RuntimeError('Don\'t know how to save more than ' +
                               'one image to VASP input')
        else:
            image = image[0]

    # Check lattice vectors are finite
    """Get unit cell parameters. Sequence of 6 numbers.

    First three are unit cell vector lengths and second three
    are angles between them::

        [len(a), len(b), len(c), angle(b,c), angle(a,c), angle(a,b)]

    in degrees.

    radians: bool, Convert angles to radians.

    See also :func:`cell.cell_to_cellpar`."""
    cellpar = cell_to_cellpar(image.lattice, radians = False)
    if np.any(cellpar == 0.):
        raise RuntimeError(
            'Lattice vectors must be finite and not coincident. '
            'At least one lattice length or angle is zero.')
    
    # Write atom positions in scaled or cartesian coordinates
    if direct and image.cartesian:                      # cartesian -> direct
        coord = image.get_scaled_positions(wrap=wrap)   
    elif not direct and not image.cartesian:            # direct -> cartesian
        coord = image._set_cartesian().position
    else:                                               # get cartesian/direct
        coord = image.position

    '''constraints = image.constraints and not ignore_constraints

    if constraints:
        sflags = np.zeros((atom_nums, 3), dtype=bool)
        for constr in image.constraints:
            if isinstance(constr, FixScaled):
                sflags[constr.a] = constr.mask
            elif isinstance(constr, FixAtoms):
                sflags[constr.index] = [True, True, True]
            elif isinstance(constr, FixedPlane):
                mask = np.all(np.abs(np.cross(constr.dir, image.cell)) < 1e-5,
                              axis=1)
                if sum(mask) != 1:
                    raise RuntimeError(
                        'VASP requires that the direction of FixedPlane '
                        'constraints is parallel with one of the cell axis')
                sflags[constr.a] = mask
            elif isinstance(constr, FixedLine):
                mask = np.all(np.abs(np.cross(constr.dir, image.cell)) < 1e-5,
                              axis=1)
                if sum(mask) != 1:
                    raise RuntimeError(
                        'VASP requires that the direction of FixedLine '
                        'constraints is parallel with one of the cell axis')
                sflags[constr.a] = ~mask'''


    if sort:
        if len(image.get_atomic_numbers()) == 0:
            atom_types_image = np.array(image.atom_types_image)
            indices_dict = {type: np.where(atom_types_image == type)[0] for type in image.atom_type}
            sorted_indices = np.concatenate([np.sort(indices) for indices in indices_dict.values()])
            symbols = atom_types_image[sorted_indices]
        else:
            sorted_indices = np.argsort(image.get_atomic_numbers())
            symbols = np.array(image.get_atomic_numbers())[sorted_indices]
        coord = np.array(coord)[sorted_indices]
        # if constraints:
        #     sflags = sflags[ind]
    else:
        symbols = image.atom_types_image
    
    # Create a list sc of (symbol, count) pairs
    if symbol_count:
        # sc = symbol_count
        pass
    elif image.atom_type_num is None:
        sc = Counter(symbols)
        atom_type = list(sc.keys())
        atom_type_num = list(sc.values())
    else:
        atom_type = image.atom_type
        atom_type_num = image.atom_type_num
        
    atom_type = [elements[_] for _ in atom_type]
    # Write to file
    output_file = open(os.path.join(data_path, data_name), 'w')
    output_file.write('Created from %s\n' % data_name)
    output_file.write('1.0\n')
    for i in range(3):
        output_file.write('%19.16f %19.16f %19.16f\n' % tuple(image.lattice[i]))
    output_file.write(' '.join(atom_type) + '\n')
    output_file.write(' '.join([str(_) for _ in atom_type_num]) + '\n')

    # if constraints:
    #     output_file.write('Selective dynamics\n')

    if direct:
        output_file.write('Direct\n')
    else:
        output_file.write('Cartesian\n')

    for i in range(atom_nums):
        output_file.write('%19.16f %19.16f %19.16f' % tuple(coord[i]))
        # if constraints:
        #     output_file.write(' %s %s %s' % tuple(sflags[i]))
        output_file.write('\n')
    output_file.close()
    print("Convert to %s successfully!" % data_name)

def write_lammps(image,
                 data_path,
                 data_name="tolammps.lmp",
                 direct=False,
                 sort=None,
                 symbol_count=None,
                 long_format=True,
                 ignore_constraints=False,
                 wrap=False):
        """Method to write LAMMPS position (lmp.init) files.
    
        Writes label, unitcell, # of various kinds of atoms,
        positions in cartesian coordinates and constraints
        to file. Cartesian coordinates is default.
        """
        atom_nums = len(image) if image.atom_nums is None else image.atom_nums
        if isinstance(image, (list, tuple)):
            if atom_nums > 1:
                raise RuntimeError('Don\'t know how to save more than ' +
                                'one image to LAMMPS input')
            else:
                image = image[0]
    
        # Check lattice vectors are finite
        """Get unit cell parameters. Sequence of 6 numbers.
    
        First three are unit cell vector lengths and second three
        are angles between them::
    
            [len(a), len(b), len(c), angle(b,c), angle(a,c), angle(a,b)]
    
        in degrees.
    
        radians: bool, Convert angles to radians.
    
        See also :func:`cell.cell_to_cellpar`."""
        cellpar = cell_to_cellpar(image.lattice, radians = False)
        if np.any(cellpar == 0.):
            raise RuntimeError(
                'Lattice vectors must be finite and not coincident. '
                'At least one lattice length or angle is zero.')
    
        # Write atom positions in cartesian coordinates
        if image.cartesian:                      # cartesian -> direct
            coord = image.get_scaled_positions(wrap=wrap)   
            image._set_orthorhombic()
        else:            # direct -> cartesian
            image._set_orthorhombic()
            coord = image._set_cartesian().position

        if sort:
            if len(image.get_atomic_numbers()) == 0:
                atom_types_image = np.array(image.atom_types_image)
                indices_dict = {type: np.where(atom_types_image == type)[0] for type in image.atom_type}
                sorted_indices = np.concatenate([np.sort(indices) for indices in indices_dict.values()])
                symbols = atom_types_image[sorted_indices]
            else:
                sorted_indices = np.argsort(image.get_atomic_numbers())
                symbols = np.array(image.get_atomic_numbers())[sorted_indices]
            coord = np.array(coord)[sorted_indices]
            # if constraints:
            #     sflags = sflags[ind]
        else:
            symbols = image.atom_types_image
        
        # Create a list sc of (symbol, count) pairs
        if symbol_count:
            # sc = symbol_count
            pass
        elif image.atom_type_num is None:
            sc = Counter(symbols)
            atom_type = list(sc.keys())
            atom_type_num = list(sc.values())
        else:
            atom_type = image.atom_type
            atom_type_num = image.atom_type_num

        p = 1
        atype = []
        # atom num & type list 
        for item in atom_type_num:
            atype += [p for _ in range(int(item))]
            p +=1

        # x array
        x = np.zeros([atom_nums,3],dtype=float)

        for idx,line in enumerate(coord):
            x[idx,0] = line[0]
            x[idx,1] = line[1]
            x[idx,2] = line[2]

        # output preparation
        # return [xx,xy,yy,xz,yz,zz]
        xlo = 0.0
        xhi = image.lattice[0][0]
        ylo = 0.0
        yhi = image.lattice[1][1]
        zlo = 0.0
        zhi = image.lattice[2][2]
        xy = image.lattice[1][0]
        xz = image.lattice[2][0]
        yz = image.lattice[2][1]

        LX = np.zeros([atom_nums,3],dtype=float)
        A = np.zeros([3,3],dtype=float)

        A[0,0] = image.lattice[0][0]
        A[1,0] = image.lattice[1][0]
        A[1,1] = image.lattice[1][1]
        A[2,0] = image.lattice[2][0]
        A[2,1] = image.lattice[2][1]
        A[2,2] = image.lattice[2][2]

        print("converted LAMMPS upper trangualr box:")
    
        print(A)
        
        # print("Ref:https://docs.lammps.org/Howto_triclinic.html")
        # convert lamda (fraction) coords x to box coords LX
        # A.T x = LX
        # LX = A*x in LAMMPS. see https://docs.lammps.org/Howto_triclinic.html

        if not image.cartesian:
            for i in range(atom_nums):
                LX[i,0] = A[0,0]*x[i,0] + A[1,0]*x[i,1] + A[2,0]*x[i,2]
                LX[i,1] = A[0,1]*x[i,0] + A[1,1]*x[i,1] + A[2,1]*x[i,2]
                LX[i,2] = A[0,2]*x[i,0] + A[1,2]*x[i,1] + A[2,2]*x[i,2]
        else:
            for i in range(atom_nums):
                LX[i,0] = x[i,0]
                LX[i,1] = x[i,1]
                LX[i,2] = x[i,2]

        # Write to file
        output_file = open(os.path.join(data_path, data_name), 'w')
        output_file.write('Created from %s\n' % data_name)
        output_file.write("%-12d atoms\n" % (atom_nums))
        output_file.write("%-12d atom types\n" % (len(atom_type)))
        output_file.write("%16.12f %16.12f xlo xhi\n" % (xlo, xhi))
        output_file.write("%16.12f %16.12f ylo yhi\n" % (ylo, yhi))
        output_file.write("%16.12f %16.12f zlo zhi\n" % (zlo, zhi))
        output_file.write("%16.12f %16.12f %16.12f xy xz yz\n" % (xy, xz, yz))
        output_file.write("\n")
        output_file.write("Masses\n")
        output_file.write("\n")
        for i in range(len(atom_type)):
            output_file.write("%-12d %16.12f # %s\n" % (i+1, ELEMENTMASSTABLE[atom_type[i]], atom_type[i]))
        output_file.write("\n")
        output_file.write("Atoms # atomic\n")
        output_file.write("\n")

        for i in range(atom_nums):
            output_file.write("%-12d %-12d %16.12f %16.12f %16.12f\n" % (i+1, atype[i], LX[i,0], LX[i,1], LX[i,2]))
        output_file.close()
        print("Convert to %s successfully!" % data_name)
            