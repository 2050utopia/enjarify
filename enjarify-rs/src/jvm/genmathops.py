# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Generate mathops.rs, the lookup tables giving information about dalvik math operations by opcode
if __name__ == "__main__":
    unary = 'ineg inot lneg lnot fneg dneg i2l i2f i2d l2i l2f l2d f2i f2l f2d d2i d2l d2f i2b i2c i2s'
    binary = 'iadd isub imul idiv irem iand ior ixor ishl ishr iushr ladd lsub lmul ldiv lrem land lor lxor lshl lshr lushr fadd fsub fmul fdiv frem dadd dsub dmul ddiv drem'
    binary = binary + ' ' + binary
    binlit = 'iadd isub imul idiv irem iand ior ixor '
    binlit = binlit + binlit + 'ishl ishr iushr'
    stypes = dict(zip('ifldbcs', 'INT FLOAT LONG DOUBLE INT INT INT'.split()))

    print('''\
// Copyright 2015 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Autogenerated by genmathops.py - do not edit''')

    print('''
use typeinference::scalar;
use super::jvmops::*;

pub struct UnaryOpInfo {
    pub op: u8,
    pub src: scalar::T,
    pub dest: scalar::T,
}

pub struct BinaryOpInfo {
    pub op: u8,
    pub src: scalar::T,
    pub src2: scalar::T,
}

pub struct Binary2OpInfo {
    pub op: u8,
}
''')

    print('const UNARY_BASE: u8 = 0x7b;')
    print('static UNARY: [UnaryOpInfo; {}] = ['.format(len(unary.split())))
    for i, code in enumerate(unary.split()):
        code = code.replace('not','xor')
        if '2' in code:
            srct = stypes[code[0]]
            destt = stypes[code[2]]
        else:
            srct = destt = stypes[code[0]]
        print('    UnaryOpInfo{{op: {}, src: scalar::{}, dest: scalar::{}}},'.format(code.upper(), srct, destt))
    print('];')

    print('const BINARY_BASE: u8 = 0x90;')
    print('static BINARY: [BinaryOpInfo; {}] = ['.format(len(binary.split())))
    for i, code in enumerate(binary.split()):
        st = stypes[code[0]]
        # shift instructions have second arg an int even when operating on longs
        st2 = 'INT' if 'sh' in code else st
        print('    BinaryOpInfo{{op: {}, src: scalar::{}, src2: scalar::{}}},'.format(code.upper(), st, st2))
    print('];')

    print('const BINARY_LIT_BASE: u8 = 0xd0;')
    print('static BINARY_LIT: [Binary2OpInfo; {}] = ['.format(len(binlit.split())))
    for i, code in enumerate(binlit.split()):
        print('    Binary2OpInfo{{op: {}}},'.format(code.upper()))
    print('];')

    print('''
pub fn unary(op: u8) -> &'static UnaryOpInfo { &UNARY[(op - UNARY_BASE) as usize] }
pub fn binary(op: u8) -> &'static BinaryOpInfo { &BINARY[(op - BINARY_BASE) as usize] }
pub fn binary_lit(op: u8) -> &'static Binary2OpInfo { &BINARY_LIT[(op - BINARY_LIT_BASE) as usize] }
''')
