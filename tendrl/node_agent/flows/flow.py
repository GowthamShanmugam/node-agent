import logging

import etcd


from tendrl.node_agent.flows import utils
from tendrl.node_agent.manager import utils as manager_utils
from tendrl.node_agent.config import TendrlConfig
from tendrl.node_agent.manager.command import Command

LOG = logging.getLogger(__name__)
config = TendrlConfig()


class Flow(object):
    def __init__(self, flow_name, job, atoms, pre_run, post_run, uuid):
        self.job = job
        self.name = flow_name
        self.atoms = atoms
        self.pre_run = pre_run
        self.post_run = post_run
        self.uuid = uuid
        self.parameters = self.job['parameters']
        self.parameters.update({'log': []})
        etcd_kwargs = {'port': int(config.get("common", "etcd_port")),
                       'host': config.get("common", "etcd_connection")}

        self.etcd_client = etcd.Client(**etcd_kwargs)
        node_agent_key = manager_utils.configure_tendrl_uuid()
        cmd = Command({"_raw_params": "cat %s" % node_agent_key})
        out, err = cmd.start()
        self.node_id = out['stdout']

    def run(self):
        post_atom = None
        pre_atom = None
        the_atom = None

        # Execute the pre runs for the flow
        LOG.info("Starting execution of pre-runs for flow: %s" %
                 self.job['run'])
        for mod in self.pre_run:
            class_name = utils.to_camel_case(mod.split(".")[-1])
            if "tendrl" in mod and "atoms" in mod:
                exec("from %s import %s as pre_atom" % (mod,
                                                        class_name))

                ret_val = pre_atom().run(self.parameters)
            if not ret_val:
                LOG.error("Failed executing pre-run: %s for flow: %s" %
                          (pre_atom, self.job['run']))
                raise Exception(
                    "Error executing pre run function: %s for flow: %s" %
                    (pre_atom, self.job['run'])
                )
            else:
                LOG.info("Successfully executed pre-run: %s for flow: %s" %
                         (pre_atom, self.job['run']))

        # Execute the atoms for the flow
        LOG.info("Starting execution of atoms for flow: %s" %
                 self.job['run'])
        for atom in self.atoms:
            class_name = utils.to_camel_case(atom.split(".")[-1])
            if "tendrl" in atom and "atoms" in atom:
                exec("from %s import %s as the_atom" % (atom,
                                                        class_name))
                ret_val = the_atom().run(self.parameters)
            if not ret_val:
                LOG.error("Failed executing atom: %s on flow: %s" %
                          (the_atom, self.job['run']))
                raise Exception(
                    "Error executing atom: %s on flow: %s" %
                    (atom, self.job['run'])
                )
            else:
                LOG.info('Successfully executed atoms for flow: %s' %
                         self.job['run'])

        # Execute the post runs for the flow
        LOG.info("Starting execution of post-runs for flow: %s" %
                 self.job['run'])
        for mod in self.post_run:
            class_name = utils.to_camel_case(mod.split(".")[-1])
            if "tendrl" in atom and "atoms" in atom:
                exec("from %s import %s as post_atom" % (
                    mod,
                    class_name)
                )

                ret_val = post_atom().run(self.parameters)

            if not ret_val:
                LOG.error("Failed executing post-run: %s for flow: %s" %
                          (post_atom, self.job['run']))
                raise Exception(
                    "Error executing post run function: %s" % post_atom
                )
            else:
                LOG.info("Successfully executed post-run: %s for flow: %s" %
                         (post_atom, self.job['run']))
