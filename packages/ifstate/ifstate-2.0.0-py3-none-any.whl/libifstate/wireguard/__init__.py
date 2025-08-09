from libifstate.util import logger, IfStateLogging
from libifstate.exception import netlinkerror_classes, FeatureMissingError
import wgnlpy
import ipaddress
import collections
from copy import deepcopy
import os
import pyroute2.netns
from pyroute2 import NetlinkError
import socket

SECRET_SETTINGS = ['private_key', 'preshared_key']

class WireGuard():
    def __init__(self, netns, iface, wireguard):
        self.netns = netns
        self.iface = iface
        self.wireguard = wireguard

        if self.netns.netns is not None:
            pyroute2.netns.pushns(self.netns.netns)

        try:
            self.wg = wgnlpy.WireGuard()
        finally:
            if self.netns.netns is not None:
                pyroute2.netns.popns()

        # convert allowedips peers settings into IPv[46]Network objects
        # and remove duplicates
        if 'peers' in self.wireguard:
            for i, peer in enumerate(self.wireguard['peers']):
                if 'allowedips' in peer:
                    self.wireguard['peers'][i]['allowedips'] = set(
                        [ipaddress.ip_network(x) for x in self.wireguard['peers'][i]['allowedips']])

    def __deepcopy__(self, memo):
        '''
        Add custom deepcopy implementation to keep single wgnlpy.WireGuard instances.
        '''
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == 'wg':
                if self.netns.netns is not None:
                    pyroute2.netns.pushns(self.netns.netns)

                try:
                    setattr(result, k, wgnlpy.WireGuard())
                finally:
                    if self.netns.netns is not None:
                        pyroute2.netns.popns()
            else:
                setattr(result, k, deepcopy(v, memo))
        return result

    def apply(self, do_apply):
        # get kernel's wireguard settings for the interface
        try:
            state = self.wg.get_interface(
                self.iface, spill_private_key=True, spill_preshared_keys=True)
        except NetlinkError as err:
            logger.warning('query wireguard details failed: {}'.format(os.strerror(err.code)), extra={'iface': self.iface, 'netns': self.netns})
            return
        except TypeError as err:
            # wgnlpy 0.1.5 can triggger a TypeError exception
            # if the WGPEER_A_LAST_HANDSHAKE_TIME NLA does not
            # return an integer
            # https://github.com/argosyLabs/wgnlpy/pull/5
            logger.warning('WireGuard on {} failed: {}'.format(
                self.iface, err.args[0]))
            # we cannot do anything here, but at least ifstate does not crash
            # with an unhandled exception from inside wgnlpy
            return

        # check base settings (not the peers, yet)
        has_changes = False
        for setting in [x for x in self.wireguard.keys() if x != 'peers']:
            logger.debug('  %s: %s => %s', setting, getattr(
                state, setting), self.wireguard[setting], extra={'iface': self.iface})
            has_changes |= self.wireguard[setting] != getattr(state, setting)

        if has_changes:
            logger.log_change('wireguard')
            if do_apply:
                try:
                    self.wg.set_interface(
                        self.iface, **{k: v for k, v in self.wireguard.items() if k != "peers"})
                except Exception as err:
                    if not isinstance(err, netlinkerror_classes):
                        raise
                    logger.warning('updating iface {} failed: {}'.format(
                        self.iface, err.args[1]))
        else:
            logger.log_ok('wireguard')

        # check peers list if provided
        if 'peers' in self.wireguard:
            peers = getattr(state, 'peers')
            has_pchanges = False

            avail = []
            for public_key, opts in self.wireguard['peers'].items():
                avail.append(public_key)
                pubkey = next(
                    iter([x for x in peers.keys() if x == public_key]), None)
                if pubkey is None:
                    has_pchanges = True
                    if do_apply:
                        try:
                            self.safe_set_peer(public_key, opts)
                        except Exception as err:
                            if not isinstance(err, netlinkerror_classes):
                                raise
                            logger.warning('add peer to {} failed: {}'.format(
                                self.iface, err.args[1]))
                else:
                    pchange = False
                    for setting in opts.keys():
                        attr = getattr(peers[pubkey], setting)
                        if setting == 'allowedips':
                            attr = [str(ip) for ip in attr]
                        logger.debug('  peer.%s: %s => %s', setting, attr,
                                     opts[setting], extra={'iface': self.iface})
                        if type(attr) == list:
                            pchange |= not (attr == opts[setting])
                        else:
                            pchange |= str(opts[setting]) != str(getattr(
                                peers[pubkey], setting))

                    if pchange:
                        has_pchanges = True
                        if do_apply:
                            try:
                                self.safe_set_peer(public_key, opts)
                            except Exception as err:
                                if not isinstance(err, netlinkerror_classes):
                                    raise
                                logger.warning('change peer at {} failed: {}'.format(
                                    self.iface, err.args[1]))

            for peer in peers:
                if not peer in avail:
                    has_pchanges = True
                    if do_apply:
                        try:
                            self.wg.remove_peers(self.iface, peer)
                        except Exception as err:
                            if not isinstance(err, netlinkerror_classes):
                                raise
                            logger.warning('remove peer from {} failed: {}'.format(
                                self.iface, err.args[1]))
            if has_pchanges:
                logger.log_change('wg.peers')
            else:
                logger.log_ok('wg.peers')

    def safe_set_peer(self, public_key, opts):
        try:
            self.wg.set_peer(self.iface, public_key=public_key, **opts)
        except (socket.gaierror, ValueError) as err:
            logger.warning('failed to set wireguard endpoint for peer {} at {}: {}'.format(public_key, self.iface, err))

            del(opts['endpoint'])
            self.wg.set_peer(self.iface, public_key=public_key, **opts)

    def show(netns, show_all, show_secrets, name, config):
        if netns.netns is not None:
            pyroute2.netns.pushns(self.netns.netns)

        try:
            wg = wgnlpy.WireGuard()
        finally:
            if netns.netns is not None:
                pyroute2.netns.popns()

        state = wg.get_interface(
            name, spill_private_key=show_secrets, spill_preshared_keys=show_secrets)

        config['wireguard'] = {
            'peers': {},
        }

        def _dump_value(value):
            if isinstance(value, (ipaddress.IPv4Network, ipaddress.IPv6Network, wgnlpy.sockaddr_in.sockaddr_in)):
                return str(value)
            elif type(value) is list:
                result = []
                for v in value:
                    result.append(_dump_value(v))
                return result
            else:
                return value

        def _dump_values(cfg, key, value):
            if show_all:
                if value is None:
                    return
            else:
                if not value:
                    return

            if key in SECRET_SETTINGS:
                if show_secrets:
                    cfg[key] = str(value)
                else:
                    cfg[key] = f"# VALUE IS HIDDEN - USE --show-secrets TO REVEAL"
            else:
                cfg[key] = _dump_value(value)

        for key in ['private_key', 'listen_port', 'fwmark']:
            value = getattr(state, key)
            _dump_values(config['wireguard'], key, value)

        for peer in state.peers:
            config['wireguard']['peers'][str(peer)] = {}
            for key in ['preshared_key', 'endpoint', 'persistent_keepalive_interval', 'allowedips']:
                value = getattr(state.peers[peer], key)
                _dump_values(config['wireguard']['peers'][str(peer)], key, value)
