#! /usr/bin/python

#
# Code generator for python ctypes bindings for VLC
# Copyright (C) 2009 the VideoLAN team
# $Id: $
#
# Authors: Olivier Aubert <olivier.aubert at liris.cnrs.fr>
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#

"""Unittest module.
"""

import unittest
import vlc
import ctypes
print "Checking ", vlc.__file__

class TestVLCAPI(unittest.TestCase):
    #def setUp(self):
    #    self.seq = range(10)
    #self.assert_(element in self.seq)

    # We check enum definitions against hardcoded values. In case of
    # failure, check that the reason is not a change in the .h
    # definitions.
    def test_enum_event_type(self):
        self.assertEqual(vlc.EventType.MediaStateChanged.value, 5)

    def test_enum_meta(self):
        self.assertEqual(vlc.Meta.Description.value, 6)

    def test_enum_state(self):
        self.assertEqual(vlc.State.Playing.value, 3)

    def test_enum_playback_mode(self):
        self.assertEqual(vlc.PlaybackMode.repeat.value, 2)

    def test_enum_marquee_int_option(self):
        self.assertEqual(vlc.VideoMarqueeOption.Size.value, 6)

    def test_enum_output_device_type(self):
        self.assertEqual(vlc.AudioOutputDeviceTypes._2F2R.value, 4)

    def test_enum_output_channel(self):
        self.assertEqual(vlc.AudioOutputChannel.Dolbys.value, 5)

    # Basic libvlc tests
    def test_instance_creation(self):
        i=vlc.Instance()
        self.assert_(i)

    def test_libvlc_media(self):
        mrl='/tmp/foo.avi'
        i=vlc.Instance()
        m=i.media_new(mrl)
        self.assertEqual(m.get_mrl(), 'file://' + mrl)

    def test_wrapper_media(self):
        mrl = '/tmp/foo.avi'
        m = vlc.Media(mrl)
        self.assertEqual(m.get_mrl(), 'file://' + mrl)

    def test_wrapper_medialist(self):
        mrl1 = '/tmp/foo.avi'
        mrl2 = '/tmp/bar.avi'
        l = vlc.MediaList( [mrl1, mrl2] )
        self.assertEqual(l[1].get_mrl(), 'file://' + mrl2)

    def test_libvlc_player(self):
        mrl='/tmp/foo.avi'
        i=vlc.Instance()
        p=i.media_player_new(mrl)
        self.assertEqual(p.get_media().get_mrl(), 'file://' + mrl)

    def test_libvlc_none_object(self):
        i=vlc.Instance()
        p=i.media_player_new()
        p.set_media(None)
        self.assertEqual(p.get_media(), None)

    def test_libvlc_player_state(self):
        mrl='/tmp/foo.avi'
        i=vlc.Instance()
        p=i.media_player_new(mrl)
        self.assertEqual(p.get_state(), vlc.State.NothingSpecial)

    def test_libvlc_logger(self):
        i=vlc.Instance()
        l=i.log_open()
        l.clear()
        self.assertEqual(l.count(), 0)
        l.close()

    def test_libvlc_logger_clear(self):
        i=vlc.Instance()
        l=i.log_open()
        l.clear()
        self.assertEqual(l.count(), 0)
        l.close()

    def test_libvlc_logger(self):
        i=vlc.Instance()
        i.set_log_verbosity(3)
        l=i.log_open()
        i.add_intf('dummy')
        for m in l:
            # Ensure that messages can be read.
            self.assertNotEqual(len(m.message), 0)
        l.close()

    def obj_ref(self, obj):
        """Get the vlc.ObjRef from vlc's object cache for the given
        obj. Returns None if the object isn't cached."""
        if not isinstance(obj, (long, int)):
            if obj._as_parameter_ is None:
                return None
            obj = obj._as_parameter_.value
        return vlc._managed_objects.get(obj)

    def test_objects_wrapped(self):
        i=vlc.Instance()
        m=i.media_new('/tmp/foo.avi')
        p=i.media_player_new()
        p.set_media(m)
        self.assertEqual(self.obj_ref(m).count, 1)
        # ensure exact same object is returned
        self.assertTrue(m is p.get_media())
        # calling p.get_media implicitly retains the returned media
        self.assertEqual(self.obj_ref(m).count, 2)
        # ensure event manager is always the same obj
        self.assertTrue(p.event_manager() is p.event_manager())

    def test_objects_retain_release(self):
        i=vlc.Instance()
        self.assertEqual(self.obj_ref(i).count, 1)
        i.retain()
        self.assertEqual(self.obj_ref(i).count, 2)
        i.retain()
        self.assertEqual(self.obj_ref(i).count, 3)
        i.release()
        self.assertEqual(self.obj_ref(i).count, 2)
        i.release()
        self.assertEqual(self.obj_ref(i).count, 1)
        i.release()
        self.assertEquals(self.obj_ref(i), None)

    def test_objects_released(self):
        i=vlc.Instance()
        p=i.media_player_new()
        m=i.media_new('/tmp/foo.avi')
        p.set_media(m)
        
        e=m.event_manager()
        self.assertFalse(e._callbacks)
        e.event_attach(vlc.EventType.MediaStateChanged, lambda x: None)
        self.assertTrue(e._callbacks)

        m.release()

        # after releasing, the callbacks should be unregistered for
        # the old event manager
        self.assertFalse(e._callbacks)
        
        # after releasing, a new python wrapper should be returned
        m2 = p.get_media()
        self.assertFalse(m is m2)
        # with a new event manager
        self.assertFalse(e is m2.event_manager())

        # after releasing, the old Media and EventManager objects
        # should be useless
        with self.assertRaises(ctypes.ArgumentError):
            m.get_mrl()

        with self.assertRaises(ctypes.ArgumentError):
            e.event_attach(vlc.EventType.MediaSubItemAdded, lambda x: None)

if __name__ == '__main__':
    unittest.main()
