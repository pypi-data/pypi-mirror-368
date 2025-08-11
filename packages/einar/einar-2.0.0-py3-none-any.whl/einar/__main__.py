# this is part of the einar project.
#
# Copyright ©  2024 - 2025 Juan Bindez  <juanbindez780@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import einar.exceptions as exception
import binascii

class AES:
    """
    Implementation of the AES (Advanced Encryption Standard) algorithm.
    Supports AES-128, AES-192, and AES-256 in ECB and CBC modes.
    Accepts shorter keys, automatically padding with zeros.
    """

    _s_box = (
        0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
        0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
        0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
        0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
        0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
        0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
        0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
        0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
        0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
        0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
        0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
        0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
        0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
        0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
        0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
        0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
    )

    _inv_s_box = (
        0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
        0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
        0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
        0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
        0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
        0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
        0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
        0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
        0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
        0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
        0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
        0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
        0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
        0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
        0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
        0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D,
    )

    _r_con = (
        0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
        0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
        0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
        0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
    )

    def __init__(self, key, keyLen=128, mode="ECB", iv=None):
        if keyLen not in (128, 192, 256):
            raise ValueError("keyLen must be 128, 192, or 256 bits")
        if mode not in ("ECB", "CBC"):
            raise ValueError("mode must be 'ECB' or 'CBC'")
        self._mode = mode
        self._keyLen = keyLen
        key_len_bytes = keyLen // 8
        if len(key) < key_len_bytes:
            key = key.ljust(key_len_bytes, b'\0')
        elif len(key) > key_len_bytes:
            key = key[:key_len_bytes]
        self._key = key
        self._n_rounds = {128: 10, 192: 12, 256: 14}[keyLen]
        self._expanded_key = self._expand_key(key)
        self._block_size = 16
        if mode == "CBC":
            if iv is None:
                raise ValueError("CBC mode requires a 16-byte IV")
            if len(iv) != 16:
                raise ValueError("IV must be 16 bytes")
            self._iv = iv

    @classmethod
    def _sub_bytes(cls, s):
        for i in range(4):
            for j in range(4):
                s[i][j] = cls._s_box[s[i][j]]

    @classmethod
    def _inv_sub_bytes(cls, s):
        for i in range(4):
            for j in range(4):
                s[i][j] = cls._inv_s_box[s[i][j]]

    @staticmethod
    def _shift_rows(s):
        # Transpose the matrix for easier row manipulation
        s = [list(row) for row in zip(*s)]
        s[1] = s[1][1:] + s[1][:1]
        s[2] = s[2][2:] + s[2][:2]
        s[3] = s[3][3:] + s[3][:3]
        # Transpose back
        return [list(row) for row in zip(*s)]

    @staticmethod
    def _inv_shift_rows(s):
        # Transpose the matrix for easier row manipulation
        s = [list(row) for row in zip(*s)]
        s[1] = s[1][3:] + s[1][:3]
        s[2] = s[2][2:] + s[2][:2]
        s[3] = s[3][1:] + s[3][:1]
        # Transpose back
        return [list(row) for row in zip(*s)]
        
    @staticmethod
    def _add_round_key(s, k):
        for i in range(4):
            for j in range(4):
                s[i][j] ^= k[i][j]

    @staticmethod
    def _gmul(a, b):
        p = 0
        while b > 0:
            if b & 1:
                p ^= a
            a = (a << 1)
            if a & 0x100:
                a ^= 0x11b
            b >>= 1
        return p

    @classmethod
    def _mix_columns(cls, s):
        for i in range(4):
            col = [s[0][i], s[1][i], s[2][i], s[3][i]]
            s[0][i] = cls._gmul(0x02, col[0]) ^ cls._gmul(0x03, col[1]) ^ col[2] ^ col[3]
            s[1][i] = col[0] ^ cls._gmul(0x02, col[1]) ^ cls._gmul(0x03, col[2]) ^ col[3]
            s[2][i] = col[0] ^ col[1] ^ cls._gmul(0x02, col[2]) ^ cls._gmul(0x03, col[3])
            s[3][i] = cls._gmul(0x03, col[0]) ^ col[1] ^ col[2] ^ cls._gmul(0x02, col[3])

    @classmethod
    def _inv_mix_columns(cls, s):
        for i in range(4):
            col = [s[0][i], s[1][i], s[2][i], s[3][i]]
            s[0][i] = cls._gmul(0x0e, col[0]) ^ cls._gmul(0x0b, col[1]) ^ cls._gmul(0x0d, col[2]) ^ cls._gmul(0x09, col[3])
            s[1][i] = cls._gmul(0x09, col[0]) ^ cls._gmul(0x0e, col[1]) ^ cls._gmul(0x0b, col[2]) ^ cls._gmul(0x0d, col[3])
            s[2][i] = cls._gmul(0x0d, col[0]) ^ cls._gmul(0x09, col[1]) ^ cls._gmul(0x0e, col[2]) ^ cls._gmul(0x0b, col[3])
            s[3][i] = cls._gmul(0x0b, col[0]) ^ cls._gmul(0x0d, col[1]) ^ cls._gmul(0x09, col[2]) ^ cls._gmul(0x0e, col[3])

    @staticmethod
    def _bytes2matrix(text):
        return [list(text[i:i+4]) for i in range(0, len(text), 4)]

    @staticmethod
    def _matrix2bytes(matrix):
        return bytes(sum(matrix, []))

    @staticmethod
    def _xor_bytes(a, b):
        return bytes(i^j for i, j in zip(a, b))

    @staticmethod
    def _pad(plaintext):
        padding_len = 16 - (len(plaintext) % 16)
        padding = bytes([padding_len] * padding_len)
        return plaintext + padding

    @staticmethod
    def _unpad(plaintext):
        if not plaintext:
            return b''
        padding_len = plaintext[-1]
        if padding_len > 16 or padding_len == 0:
            raise exception.PaddingError("Invalid padding")
        message, padding = plaintext[:-padding_len], plaintext[-padding_len:]
        if not all(p == padding_len for p in padding):
            raise exception.PaddingError("Invalid padding")
        return message

    @staticmethod
    def _split_blocks(message, block_size=16):
        return [message[i:i+16] for i in range(0, len(message), 16)]

    @classmethod
    def _rot_word(cls, word):
        return word[1:] + word[:1]

    @classmethod
    def _sub_word(cls, word):
        return [cls._s_box[b] for b in word]

    @classmethod
    def _expand_key(cls, master_key):
        key_len = len(master_key)
        assert key_len in (16, 24, 32)
        n_rounds = {16: 10, 24: 12, 32: 14}[key_len]
        key_words = [list(master_key[i:i+4]) for i in range(0, len(master_key), 4)]
        
        i = 1
        while len(key_words) < (n_rounds + 1) * 4:
            temp = list(key_words[-1])
            if len(key_words) % (key_len // 4) == 0:
                temp = cls._rot_word(temp)
                temp = cls._sub_word(temp)
                temp[0] ^= cls._r_con[i]
                i += 1
            elif key_len == 32 and len(key_words) % (key_len // 4) == 4:
                temp = cls._sub_word(temp)
            
            prev_word = key_words[len(key_words) - (key_len // 4)]
            new_word = [temp[j] ^ prev_word[j] for j in range(4)]
            key_words.append(new_word)
        
        expanded_key = []
        for i in range(n_rounds + 1):
            round_key = [key_words[4*i], key_words[4*i+1], key_words[4*i+2], key_words[4*i+3]]
            expanded_key.append(round_key)
        
        return expanded_key

    def _encrypt_block(self, plaintext):
        state = self._bytes2matrix(plaintext)
        self._add_round_key(state, self._expanded_key[0])
        for i in range(1, self._n_rounds):
            self._sub_bytes(state)
            state = self._shift_rows(state)
            self._mix_columns(state)
            self._add_round_key(state, self._expanded_key[i])
        self._sub_bytes(state)
        state = self._shift_rows(state)
        self._add_round_key(state, self._expanded_key[self._n_rounds])
        return self._matrix2bytes(state)

    def _decrypt_block(self, ciphertext):
        state = self._bytes2matrix(ciphertext)
        self._add_round_key(state, self._expanded_key[self._n_rounds])
        state = self._inv_shift_rows(state)
        self._inv_sub_bytes(state)
        for i in range(self._n_rounds - 1, 0, -1):
            self._add_round_key(state, self._expanded_key[i])
            self._inv_mix_columns(state)
            state = self._inv_shift_rows(state)
            self._inv_sub_bytes(state)
        self._add_round_key(state, self._expanded_key[0])
        return self._matrix2bytes(state)

    def encrypt_ecb(self, plaintext):
        plaintext = self._pad(plaintext)
        blocks = []
        for plaintext_block in self._split_blocks(plaintext):
            blocks.append(self._encrypt_block(plaintext_block))
        return b''.join(blocks)

    def decrypt_ecb(self, ciphertext):
        blocks = []
        for ciphertext_block in self._split_blocks(ciphertext):
            blocks.append(self._decrypt_block(ciphertext_block))
        return self._unpad(b''.join(blocks))

    def encrypt(self, plaintext):
        if self._mode == "ECB":
            return self.encrypt_ecb(plaintext)
        elif self._mode == "CBC":
            return self.encrypt_cbc(plaintext)

    def decrypt(self, ciphertext):
        if self._mode == "ECB":
            return self.decrypt_ecb(ciphertext)
        elif self._mode == "CBC":
            return self.decrypt_cbc(ciphertext)

    def encrypt_cbc(self, plaintext):
        plaintext = self._pad(plaintext)
        blocks = []
        prev = self._iv
        for plaintext_block in self._split_blocks(plaintext):
            block = self._xor_bytes(plaintext_block, prev)
            encrypted_block = self._encrypt_block(block)
            blocks.append(encrypted_block)
            prev = encrypted_block
        return b''.join(blocks)

    def decrypt_cbc(self, ciphertext):
        blocks = []
        prev = self._iv
        for ciphertext_block in self._split_blocks(ciphertext):
            decrypted_block = self._decrypt_block(ciphertext_block)
            block = self._xor_bytes(decrypted_block, prev)
            blocks.append(block)
            prev = ciphertext_block
        return self._unpad(b''.join(blocks))