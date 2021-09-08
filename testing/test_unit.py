# (c) Copyright 2020 by Coinkite Inc. This file is covered by license found in COPYING-CC.
#
# Run tests on the simulator itself, not here... these are basically "unit tests"
#
import pytest, glob
from helpers import B2A
from binascii import b2a_hex, a2b_hex

def test_remote_exec(sim_exec):
    assert sim_exec("RV.write('testing123')") == 'testing123'

def test_codecs(sim_execfile):
    assert sim_execfile('devtest/segwit_addr.py') == ''

def test_public(sim_execfile):
    "verify contents of public 'dump' file"
    from pycoin.key.BIP32Node import BIP32Node
    from pycoin.contrib.segwit_addr import encode as sw_encode
    from pycoin.contrib.segwit_addr import decode as sw_decode
    from pycoin.encoding import a2b_hashed_base58, hash160

    pub = sim_execfile('devtest/dump_public.py')
    assert 'Error' not in pub

    #print(pub)

    pub, dev = pub.split('#DEBUG#', 1)
    assert 'pub' in pub
    assert 'prv' not in pub
    assert 'prv' in dev

    lines = [i.strip() for i in pub.split('\n')]

    for ln in lines:
        if ln[1:4] == 'pub':
            node_pub = BIP32Node.from_wallet_key(ln)
            break

    node_prv = BIP32Node.from_wallet_key(dev.strip())

    # pub and private are linked
    assert node_prv.hwif(as_private=False) == node_pub.hwif()

    # check every path we derived
    count = 0
    for ln in lines:
        if ln[0:1] == 'm' and '=>' in ln:
            subpath, result = ln.split(' => ', 1)

            sk = node_prv.subkey_for_path(subpath[2:])

            if result[1:4] == 'pub' and result[0] not in 'xt':
                # SLIP-132 garbage
                assert 'SLIP-132' in result
                result = result.split('#', 1)[0].strip()

                # just base58/checksum check
                assert a2b_hashed_base58(result)

            elif result[1:4] == 'pub':
                try:
                    expect = BIP32Node.from_wallet_key(result)
                except Exception as e:
                    if 'unknown prefix' in str(e):
                        # pycoin not yet ready for SLIP-132
                        assert result[0] != 'x'
                        print("SKIP: " + ln)
                        continue
                    raise
                assert sk.hwif(as_private=False) == result
            elif result[0] in '1mn':
                assert result == sk.address(False)
            elif result[0:3] in { 'bc1', 'tb1' }:
                h20 = sk.hash160()
                assert result == sw_encode(result[0:2], 0, h20)
            elif result[0] in '23':
                h20 = hash160(b'\x00\x14' + sk.hash160())
                assert h20 == a2b_hashed_base58(result)[1:]
            else:
                raise ValueError(result)

            count += 1
            print("OK: %s" % ln)
            

    assert count > 12


def test_nvram(unit_test):
    # exercise nvram simulation
    unit_test('devtest/nvram.py')

@pytest.mark.parametrize('mode', ['simple', 'blankish'])
def test_backups(unit_test, mode, set_seed_words):
    # exercise dump of pub data
    if mode == 'blankish':
        # want a zero in last byte of hex representation of raw secret...
        '''
        >>> tcc.bip39.from_data(bytes([0x10]*32))
        'avoid letter advice cage ... absurd amount doctor blanket'
        '''
        set_seed_words('avoid letter advice cage absurd amount doctor acoustic avoid letter advice cage absurd amount doctor acoustic avoid letter advice cage absurd amount doctor blanket')

    unit_test('devtest/backups.py')

def test_bip143(unit_test):
    # exercise hash digesting for bip143 signatures
    unit_test('devtest/unit_bip143.py')

def test_addr_decode(unit_test):
    # - runs som known examples thru CTxIn and check it categories, and extracts pubkey/pkh right
    unit_test('devtest/unit_addrs.py')

def test_clear_seed(unit_test):
    # just testing the test?
    unit_test('devtest/clear_seed.py')

def test_slip132(unit_test):
    # slip132 ?pub stuff
    unit_test('devtest/unit_slip132.py')

def test_multisig(unit_test):
    # scripts/multisig unit tests
    unit_test('devtest/unit_multisig.py')

def test_decoding(unit_test):
    # utils.py Hex/Base64 streaming decoders
    unit_test('devtest/unit_decoding.py')

@pytest.mark.parametrize('hasher', ['sha256', 'sha1', 'sha512'])
@pytest.mark.parametrize('msg', [b'123', b'b'*78])
@pytest.mark.parametrize('key', [b'3245', b'b'*78])
def test_hmac(sim_exec, msg, key, hasher):
    import hashlib, hmac

    cmd = "import ngu; from h import b2a_hex; " + \
                    f"RV.write(b2a_hex(ngu.hmac.hmac_{hasher}({key}, {msg})))"
    print(cmd)

    got = sim_exec(cmd)
    expect = hmac.new(key, msg, hasher).hexdigest()

    assert got == expect
    #print(expect)

@pytest.mark.parametrize('secret,counter,expect', [
        ( b'abcdefghij', 1, '765705'),
        ( b'abcdefghij', 2, '816065'),
		( b'12345678901234567890', 0, '755224'),    # test vectors from RFC4226
		( b'12345678901234567890', 1, '287082'),
		( b'12345678901234567890', 2, '359152'),
		( b'12345678901234567890', 3, '969429'),
		( b'12345678901234567890', 4, '338314'),
		( b'12345678901234567890', 5, '254676'),
		( b'12345678901234567890', 6, '287922'),
		( b'12345678901234567890', 7, '162583'),
		( b'12345678901234567890', 8, '399871'),
		( b'12345678901234567890', 9, '520489'),
])
def test_hotp(sim_exec, secret, counter, expect):
    cmd = "from users import calc_hotp; " + \
                    f"RV.write(calc_hotp({secret}, {counter}))"
    got = sim_exec(cmd)
    assert got == expect

def test_hmac_key(dev, sim_exec, count=10):
    from hashlib import pbkdf2_hmac, sha256
    from ckcc_protocol.constants import PBKDF2_ITER_COUNT

    sn = sim_exec('import version; RV.write(version.serial_number().encode())').encode()
    salt = sha256(b'pepper'+sn).digest()

    for i in range(count):
        pw = ('test%09d' % i).encode('ascii')
        pw = pw[1:i] if i > 2 else pw
        cmd = "from users import calc_hmac_key; from h import b2a_hex; " + \
                    f"RV.write(b2a_hex(calc_hmac_key({pw})))"

        got = sim_exec(cmd)

        #print('pw=%r s=%r cnt=%d' % (pw, salt, PBKDF2_ITER_COUNT))
        expect = B2A(pbkdf2_hmac('sha512', pw, salt, PBKDF2_ITER_COUNT)[0:32])

        assert got == expect
        print(got)

@pytest.mark.parametrize('path,ans', [
    ("m", "m"),
    ("", "m"),
    ("55555p/66666", "m/55555'/66666"),
    ("m/1/2/3", "m/1/2/3"),
    ("m/1'/2h/3p/4H/5P", "m/1'/2'/3'/4'/5'"),
    ("m/1'/2h/3p/4H/*'", "m/1'/2'/3'/4'/*'"),
    ("m/1'/2h/3p/4H/*", "m/1'/2'/3'/4'/*"),
    ("m/10000000/5'/*", "m/10000000/5'/*"),
])
@pytest.mark.parametrize('star', [False, True])
def test_cleanup_deriv_path_good(path, ans, star, sim_exec):

    cmd = f'from utils import cleanup_deriv_path; RV.write(cleanup_deriv_path({repr(path)}, allow_star={star}))'
    rv = sim_exec(cmd)

    if not star and '*' in path:
        assert 'Traceback' in rv
        assert 'invalid characters' in rv
    else:
        assert rv == ans

@pytest.mark.parametrize('path,ans', [
    ("m/", "empty path component"),
    ("m//", "empty path component"),
    ("m/*/*", "invalid characters"),
    ("m/4/100000000000000", "bad component"),
    ("m/100000000000000/*", "bad component"),
    ("m/-34/*", "invalid characters"),
    ("m/*/5/*", "invalid characters"),
    ("m/*/*", "invalid characters"),
    ("m/*/5", "invalid characters"),
])
def test_cleanup_deriv_path_fails(path, ans, sim_exec, star=True):

    cmd = f'from utils import cleanup_deriv_path; RV.write(cleanup_deriv_path({repr(path)}, allow_star={star}))'
    rv = sim_exec(cmd)

    assert 'Traceback' in rv
    assert ans in rv
    

@pytest.mark.parametrize('patterns, paths, answers', [
    (["m"], ("m", "m/2", "*", "any"), [True, False, False, False]),
    (["any"], ("m", "m/2", "*", "1/2/3/4/5/6'/55'"), [True]*4),
    (["m/1", "m/2/*'"], ("m", "m/1", "m/3/4", "m/2/4'", "m/2/4"), 
                        [0,    1,    0,       1,        0]),
    (["m/1/*", "m/2/*'"], ("m/1/2", "m/1/2'", "m/2/1", "m/2/1'"), 
                           [1,       0,       0,       1]),
])
def test_match_deriv_path(patterns, paths, answers, sim_exec):
    for path, ans in zip(paths, answers):
        cmd = f'from utils import match_deriv_path; RV.write(str(match_deriv_path({repr(patterns)}, {repr(path)})))'
        rv = sim_exec(cmd)
        assert rv == str(bool(ans))
    
@pytest.mark.parametrize('case', range(6))
def test_ndef(case, load_shared_mod):
    # NDEF unit tests
    import ndef
    from struct import pack, unpack
    from binascii import b2a_hex

    def get_body(efile):
        # unwrap CC_FILE and cruft
        assert efile[-1] == 0xfe
        assert efile[0] == 0xE2
        st = len(cc_ndef.CC_FILE)
        if efile[st] == 0xff:
            xl = unpack('>H', efile[st+1:st+3])[0]
            st += 3
        else:
            xl = efile[st]
            st += 1
        body = efile[st:-1]
        assert len(body) == xl
        return body

    def decode(msg):
        return list(ndef.message_decoder(get_body(msg)))

    cc_ndef = load_shared_mod('cc_ndef', '../shared/ndef.py')
    n = cc_ndef.ndefMaker()

    if case == 0:
        n.add_text("Hello world")

        got, = decode(n.bytes())
        assert got.type == 'urn:nfc:wkt:T'
        assert got.text == 'Hello world'
        assert got.language == 'en'
        assert got.encoding == 'UTF-8'

    elif case == 1:
        n.add_text("Hello world")
        n.add_url("store.coinkite.com/store/coldcard")
        
        txt,url = decode(n.bytes())
        assert txt.text == 'Hello world'

        assert url.type == 'urn:nfc:wkt:U'
        assert url.uri == 'https://store.coinkite.com/store/coldcard' == url.iri

    elif case == 2:
        hx = b2a_hex(bytes(range(32)))
        n.add_text("Title")
        n.add_custom('bitcoin.org:sha256', hx)

        txt,sha = decode(n.bytes())
        assert txt.text == 'Title'
        assert sha.data == hx

    elif case == 3:
        psbt = b'psbt\xff' + bytes(5000)
        n.add_text("Title")
        n.add_custom('bitcoin.org:psbt', psbt)
        n.add_text("Footer")

        txt,p,ft = decode(n.bytes())
        assert txt.text == 'Title'
        assert ft.text == 'Footer'
        assert p.data == psbt
        assert p.type == 'urn:nfc:ext:bitcoin.org:psbt'

    elif case == 4:
        hx = b2a_hex(bytes(range(32)))
        n.add_custom('bitcoin.org:txid', hx)
        got, = decode(n.bytes())
        assert got.type == 'urn:nfc:ext:bitcoin.org:txid'
        assert got.data == hx

    elif case == 5:
        hx = bytes(2000)
        n.add_custom('bitcoin.org:txn', hx)
        got, = decode(n.bytes())
        assert got.type == 'urn:nfc:ext:bitcoin.org:txn'
        assert got.data == hx

@pytest.mark.parametrize('ccfile', [
    'E1 40 80 09  03 10  D1 01 0C 55 01 6E 78 70 2E 63 6F 6D 2F 6E 66 63 FE 00', 
    'E1 40 40 00  03 2A   D1012655016578616D706C652E636F6D2F74656D703D303030302F746170636F756E7465723D30303030FE000000',
    b'\xe1@@\x00\x03*\xd1\x01&U\x01example.com/temp=0000/tapcounter=0000\xfe\x00\x00\x00',
    'rx',
    'short',
    'long',
])
def test_ndef_ccfile(ccfile, load_shared_mod):
    # NDEF unit tests
    import ndef
    from struct import pack, unpack
    from binascii import b2a_hex

    def decode(body):
        return list(ndef.message_decoder(body))

    cc_ndef = load_shared_mod('cc_ndef', '../shared/ndef.py')

    txt_msg = None
    if ccfile == 'rx':
        ccfile = cc_ndef.CC_WR_FILE
    elif ccfile == 'short':
        n = cc_ndef.ndefMaker()
        txt_msg = "this is a test"
        n.add_text(txt_msg)
        ccfile = n.bytes()
    elif ccfile == 'long':
        n = cc_ndef.ndefMaker()
        txt_msg = "t" * 600
        n.add_text(txt_msg)
        ccfile = n.bytes()
    elif isinstance(ccfile, str):
        ccfile = a2b_hex(ccfile.replace(' ', ''))
    
    st, ll, is_wr, mlen = cc_ndef.ccfile_decode(ccfile[0:16])
    assert ccfile[st+ll] == 0xfe
    body = ccfile[st:st+ll]
    ref = decode(body)

    if ll == 0: return      # empty we can't parse

    got = list(cc_ndef.record_parser(body))

    for r,g in zip(ref, got):
        assert r.type == g[0]
        urn, data, meta = g
        if r.type == 'urn:nfc:wkt:U':
            assert r.data == bytes([meta['prefix']]) + bytes(data)
        if r.type == 'urn:nfc:wkt:T':
            assert data == r.text.encode('utf-8')
            assert meta['lang'] == 'en'
            if txt_msg:
                assert data == txt_msg.encode('utf-8')

# EOF
